# MOESI_MCN.py
# Author: Masashi Oda <oda@lab3.kuis.kyoto-u.ac.jp>

import math
import m5
from m5.objects import *
from m5.defines import buildEnv
from .Ruby import create_topology, create_directories
from .Ruby import send_evicts

from common import ObjectList
from common import MemConfig

#
# Declare caches used by the protocol
#
class L1Cache(RubyCache):
    dataAccessLatency = 1
    tagAccessLatency = 1


class L2Cache(RubyCache):
    dataAccessLatency = 20
    tagAccessLatency = 20


def define_options(parser):
    return


def create_system(
    options, full_system, system, dma_ports, bootmem, ruby_system, cpus
):

    cpu_sequencers = []

    #
    # The ruby network creation expects the list of nodes in the system to be
    # consistent with the NetDest list.  Therefore the l1 controller nodes must be
    # listed before the directory nodes and directory nodes before dma nodes, etc.
    #
    l1_cntrl_nodes = []
    l2_cntrl_nodes = []
    dir_cntrl_nodes = []
    dma_cntrl_nodes = []

    corner_nodes = [0, 5, 10, 15]

    #
    # Must create the individual controllers before the network to ensure the
    # controller constructors are called before the network constructor
    #
    block_size_bits = int(math.log(options.cacheline_size, 2)) # 6

    for i in range(options.num_cpus):
        #
        # First create the Ruby objects associated with this cpu
        #
        l1i_cache = L1Cache(
            size=options.l1i_size,
            assoc=options.l1i_assoc,
            start_index_bit=block_size_bits,
            is_icache=True,
        )
        l1d_cache = L1Cache(
            size=options.l1d_size,
            assoc=options.l1d_assoc,
            start_index_bit=block_size_bits,
            is_icache=False,
        )

        clk_domain = cpus[i].clk_domain

        l1_cntrl = L1Cache_Controller(
            version=i,
            L1Icache=l1i_cache,
            L1Dcache=l1d_cache,
            send_evictions=send_evicts(options),
            transitions_per_cycle=options.ports,
            clk_domain=clk_domain,
            ruby_system=ruby_system,
        )

        cpu_seq = RubySequencer(
            version=i,
            dcache=l1d_cache,
            clk_domain=clk_domain,
            ruby_system=ruby_system,
        )

        l1_cntrl.sequencer = cpu_seq
        exec("ruby_system.l1_cntrl%d = l1_cntrl" % i)

        # Add controllers and sequencers to the appropriate lists
        cpu_sequencers.append(cpu_seq)
        l1_cntrl_nodes.append(l1_cntrl)

        # Connect the L1 controllers and the network
        l1_cntrl.mandatoryQueue = MessageBuffer()
        l1_cntrl.requestFromL1Cache = MessageBuffer()
        l1_cntrl.requestFromL1Cache.out_port = ruby_system.network.in_port
        l1_cntrl.responseFromL1Cache = MessageBuffer()
        l1_cntrl.responseFromL1Cache.out_port = ruby_system.network.in_port
        l1_cntrl.requestToL1Cache = MessageBuffer()
        l1_cntrl.requestToL1Cache.in_port = ruby_system.network.out_port
        l1_cntrl.responseToL1Cache = MessageBuffer()
        l1_cntrl.responseToL1Cache.in_port = ruby_system.network.out_port
        l1_cntrl.triggerQueue = MessageBuffer(ordered=True)

    # Create the L2s interleaved addr ranges
    l2_addr_ranges = []
    l2_bits = int(math.log(options.num_l2caches, 2)) # l2_bits = 2
    numa_bit = block_size_bits + l2_bits - 1         # numa_bit = 7
    sysranges = [] + system.mem_ranges
    for i in range(options.num_l2caches):
        ranges = []
        for r in sysranges:
            addr_range = AddrRange(
                r.start,
                size=r.size(),
                intlvHighBit=numa_bit,
                intlvBits=l2_bits,
                intlvMatch=i,
            )
            ranges.append(addr_range)
        l2_addr_ranges.append(ranges)

    for i in range(options.num_l2caches):
        #
        # First create the Ruby objects associated with this cpu
        #
        l2_cache = L2Cache(
            size=options.l2_size,
            assoc=options.l2_assoc,
            start_index_bit=block_size_bits + l2_bits,
        )

        l2_cntrl = L2Cache_Controller(
            version=i,
            L2cache=l2_cache,
            transitions_per_cycle=options.ports,
            ruby_system=ruby_system,
            addr_ranges=l2_addr_ranges[i],
        )

        exec("ruby_system.l2_cntrl%d = l2_cntrl" % i)
        l2_cntrl_nodes.append(l2_cntrl)

        # Connect the L2 controllers and the network
        l2_cntrl.GlobalRequestFromL2Cache = MessageBuffer()
        l2_cntrl.GlobalRequestFromL2Cache.out_port = (
            ruby_system.network.in_port
        )
        l2_cntrl.L1RequestFromL2Cache = MessageBuffer()
        l2_cntrl.L1RequestFromL2Cache.out_port = ruby_system.network.in_port
        l2_cntrl.responseFromL2Cache = MessageBuffer()
        l2_cntrl.responseFromL2Cache.out_port = ruby_system.network.in_port

        l2_cntrl.GlobalRequestToL2Cache = MessageBuffer()
        l2_cntrl.GlobalRequestToL2Cache.in_port = ruby_system.network.out_port
        l2_cntrl.L1RequestToL2Cache = MessageBuffer()
        l2_cntrl.L1RequestToL2Cache.in_port = ruby_system.network.out_port
        l2_cntrl.responseToL2Cache = MessageBuffer()
        l2_cntrl.responseToL2Cache.in_port = ruby_system.network.out_port
        l2_cntrl.triggerQueue = MessageBuffer(ordered=True)

    # Run each of the ruby memory controllers at a ratio of the frequency of
    # the ruby system.
    # clk_divider value is a fix to pass regression.
    ruby_system.memctrl_clk_domain = DerivedClockDomain(
        clk_domain=ruby_system.clk_domain, clk_divider=3
    )

    mem_dir_cntrl_nodes, rom_dir_cntrl_node = create_directories(
        options, bootmem, ruby_system, system
    )
    mem_ctrl = []
    dir_cntrl_nodes = mem_dir_cntrl_nodes[:]
    if rom_dir_cntrl_node is not None:
        dir_cntrl_nodes.append(rom_dir_cntrl_node)
    for (i, dir_cntrl) in enumerate(dir_cntrl_nodes):
        # Connect the directory controllers and the network
        dir_cntrl.requestToDir = MessageBuffer()
        dir_cntrl.requestToDir.in_port = ruby_system.network.out_port
        dir_cntrl.responseToDir = MessageBuffer()
        dir_cntrl.responseToDir.in_port = ruby_system.network.out_port
        dir_cntrl.responseFromDir = MessageBuffer()
        dir_cntrl.responseFromDir.out_port = ruby_system.network.in_port
        dir_cntrl.forwardFromDir = MessageBuffer()
        dir_cntrl.forwardFromDir.out_port = ruby_system.network.in_port
        dir_cntrl.requestToMemory = MessageBuffer()
        dir_cntrl.responseFromMemory = MessageBuffer()
        dir_cntrl.triggerQueue = MessageBuffer(ordered=True)

        ruby_system.block_size_bytes = options.cacheline_size
        ruby_system.memory_size_bits = 48
        intlv_size = options.cacheline_size

        dir_ranges = []
        for r in system.mem_ranges:
            mem_type = ObjectList.mem_list.get(options.mem_type)
            # create_mem_intf(intf, r, i, intlv_bits, intlv_size, xor_low_bit)
            dram_intf = MemConfig.create_mem_intf(
                mem_type,
                r,
                i,
                int(math.log(options.num_dirs, 2)), # ？保留
                intlv_size,
                options.xor_low_bit,
            )
            mem_ctrl = m5.objects.MemCtrl(dram=dram_intf)

            dir_ranges.append(dram_intf.range)

            mem_ctrl.port = dir_cntrl.memory_out_port

            # Enable low-power DRAM states if option is set
            if issubclass(mem_type, DRAMInterface):
                mem_ctrl.dram.enable_dram_powerdown = (options.enable_dram_powerdown)

        dir_cntrl.addr_ranges = dir_ranges
        print(dir_ranges)

        system.mem_ctrls = mem_ctrls


    for i, dma_port in enumerate(dma_ports):
        #
        # Create the Ruby objects associated with the dma controller
        #
        dma_seq = DMASequencer(
            version=i, ruby_system=ruby_system, in_ports=dma_port
        )

        dma_cntrl = DMA_Controller(
            version=i,
            dma_sequencer=dma_seq,
            transitions_per_cycle=options.ports,
            ruby_system=ruby_system,
        )

        exec("ruby_system.dma_cntrl%d = dma_cntrl" % i)
        dma_cntrl_nodes.append(dma_cntrl)

        # Connect the dma controller to the network
        dma_cntrl.mandatoryQueue = MessageBuffer()
        dma_cntrl.responseFromDir = MessageBuffer()
        dma_cntrl.responseFromDir.in_port = ruby_system.network.out_port
        dma_cntrl.reqToDir = MessageBuffer()
        dma_cntrl.reqToDir.out_port = ruby_system.network.in_port
        dma_cntrl.respToDir = MessageBuffer()
        dma_cntrl.respToDir.out_port = ruby_system.network.in_port
        dma_cntrl.triggerQueue = MessageBuffer(ordered=True)

    all_cntrls = (
        l1_cntrl_nodes + l2_cntrl_nodes + dir_cntrl_nodes + mem_ctrl_nodes + dma_cntrl_nodes
    )

    # Create the io controller and the sequencer
    if full_system:
        io_seq = DMASequencer(version=len(dma_ports), ruby_system=ruby_system)
        ruby_system._io_port = io_seq
        io_controller = DMA_Controller(
            version=len(dma_ports),
            dma_sequencer=io_seq,
            ruby_system=ruby_system,
        )
        ruby_system.io_controller = io_controller

        # Connect the dma controller to the network
        io_controller.mandatoryQueue = MessageBuffer()
        io_controller.responseFromDir = MessageBuffer()
        io_controller.responseFromDir.in_port = ruby_system.network.out_port
        io_controller.reqToDir = MessageBuffer()
        io_controller.reqToDir.out_port = ruby_system.network.in_port
        io_controller.respToDir = MessageBuffer()
        io_controller.respToDir.out_port = ruby_system.network.in_port
        io_controller.triggerQueue = MessageBuffer(ordered=True)

        all_cntrls = all_cntrls + [io_controller]

    ruby_system.network.number_of_virtual_networks = 3
    topology = create_topology(all_cntrls, options)
    return (cpu_sequencers, dir_cntrl_nodes, topology)
