# fs_x86_mcn.py
# Author: Masashi Oda

# Full System Simulation config file
# ISA: x86
# Memory Cube Network architecture

"""
Usage:

$ scons ./build/X86/gem5.opt -j5
$ ./fs.sh

"""

import argparse
import math
import sys

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import *

addToPath("../")

from ruby import Ruby

from common.FSConfig import *
from common.SysPaths import *
from common.Benchmarks import *
from common import Simulation
from common import ObjectList
from common.Caches import *
from common import Options
from common import FileSystemConfig
from common import HMC

from topologies import *
from network import Network

# ----------------------------- Add Options ---------------------------- #
parser = argparse.ArgumentParser()
Options.addCommonOptions(parser)
Options.addFSOptions(parser)
Ruby.define_options(parser)
HMC.add_options(parser)

# ---------------------------- Parse Options --------------------------- #
args = parser.parse_args()

# CPU and Memory
(CPUClass, mem_mode, FutureClass) = Simulation.setCPUClass(args)
MemClass = Simulation.setMemClass(args)

# makeLinuxX86System(mem_mode, args.num_cpus, mdesc, args.ruby, cmdline=cmdline)
# ---------------------------- Setup System ---------------------------- #
system = System()
# System -> src/sim/System.py

system.m5ops_base = 0x0_FFFF_0000

workload = X86FsLinux()
if workload is None:
    workload = X86FsWorkload()
system.workload = workload
# X86FsLinux, X86FsWorkload -> src/arch/x86/X88FsWorkload.py

mdesc = SysConfig(
    disks=args.disk_image,
    rootdev=args.root_device,
    mem=args.mem_size,
    os_type=args.os_type,
)
system.readfile = mdesc.script()

system.mem_mode = mem_mode

# ----------------- Memory Address Range Setup ----------------- #
hmc_size = convert.toMemorySize("512MB")
mem_size = convert.toMemorySize(args.mem_size)

addr_ranges = []
sl_ranges = []
vault_ranges = []

for idx in range(args.num_mems):
    addr_range = AddrRange(
            start=0, 
            size=mem_size,
            masks=[
                0x0_0010_0000,
                0x0_0020_0000,
                0x0_0040_0000, 
                0x0_0080_0000,
            ],
            intlvMatch=idx
    )
    addr_ranges.append(addr_range)
    
    for i in range(args.num_serial_links): # i = 0..3
        sl_range = AddrRange(
            start=0, 
            size=mem_size,
            masks=[
                0x0_0000_1000,
                0x0_0000_2000,
                0x0_0010_0000,
                0x0_0020_0000,
                0x0_0040_0000, 
                0x0_0080_0000,
            ],
            intlvMatch=(idx * args.num_serial_links + i)
        )
        sl_ranges.append(sl_range)


    print("hmc%02d" % idx)
    for i in range(args.hmc_dev_num_vaults): # i = 0..15
        vault_range = AddrRange(
            start=0, 
            size=mem_size,
            masks=[
                0x0_0000_0400,
                0x0_0000_0800,
                0x0_0000_1000,
                0x0_0000_2000,
                0x0_0010_0000,
                0x0_0020_0000,
                0x0_0040_0000, 
                0x0_0080_0000,
            ],
            intlvMatch=(idx * args.hmc_dev_num_vaults + i),
        )
        vault_ranges.append(vault_range)
        print("  vault%02d: %s" % (i, vault_range))

system.mem_ranges = addr_ranges

# -------------------------------------------------------------- #

# Platform
system.pc = Pc()
# Pc -> src/dev/x86/Pc.py

# North Bridge
system.iobus = IOXBar()
# IOXBae -> src/mem/XBar.py

# add the IDE to the list of DMA devices that later need to attach to dma controllers
system._dma_ports = [system.pc.south_bridge.ide.dma]
system.pc.attachIO(system.iobus, system._dma_ports)

# Disks
disks = makeCowDisks(mdesc.disks())
system.pc.south_bridge.ide.disks = disks

# Add in a Bios information structure.
structures = [X86SMBiosBiosInformation()]
workload.smbios_table.structures = structures
# X86SMBiosBiosInformation -> src/arch/x86/bios/SMBios.py

# --------------------- Set up the Intel MP table ----------------------- #
base_entries = []
ext_entries = []
madt_records = []
for i in range(args.num_cpus):
    bp = X86IntelMPProcessor(
        local_apic_id=i,
        local_apic_version=0x14,
        enable=True,
        bootstrap=(i == 0),
    )
    base_entries.append(bp)
    lapic = X86ACPIMadtLAPIC(acpi_processor_id=i, apic_id=i, flags=1)
    madt_records.append(lapic)
io_apic = X86IntelMPIOAPIC(
    id=args.num_cpus, version=0x11, enable=True, address=0x0_FEC0_0000
)
system.pc.south_bridge.io_apic.apic_id = io_apic.id
base_entries.append(io_apic)
madt_records.append(
    X86ACPIMadtIOAPIC(id=io_apic.id, address=io_apic.address, int_base=0)
)
# In gem5 Pc::calcPciConfigAddr(), it required "assert(bus==0)",
# but linux kernel cannot config PCI device if it was not connected to
# PCI bus, so we fix PCI bus id to 0, and ISA bus id to 1.
pci_bus = X86IntelMPBus(bus_id=0, bus_type="PCI   ")
base_entries.append(pci_bus)
isa_bus = X86IntelMPBus(bus_id=1, bus_type="ISA   ")
base_entries.append(isa_bus)
connect_busses = X86IntelMPBusHierarchy(
    bus_id=1, subtractive_decode=True, parent_bus=0
)
ext_entries.append(connect_busses)
pci_dev4_inta = X86IntelMPIOIntAssignment(
    interrupt_type="INT",
    polarity="ConformPolarity",
    trigger="ConformTrigger",
    source_bus_id=0,
    source_bus_irq=0 + (4 << 2),
    dest_io_apic_id=io_apic.id,
    dest_io_apic_intin=16,
)
base_entries.append(pci_dev4_inta)
pci_dev4_inta_madt = X86ACPIMadtIntSourceOverride(
    bus_source=pci_dev4_inta.source_bus_id,
    irq_source=pci_dev4_inta.source_bus_irq,
    sys_int=pci_dev4_inta.dest_io_apic_intin,
    flags=0,
)
madt_records.append(pci_dev4_inta_madt)

def assignISAInt(irq, apicPin):
    assign_8259_to_apic = X86IntelMPIOIntAssignment(
        interrupt_type="ExtInt",
        polarity="ConformPolarity",
        trigger="ConformTrigger",
        source_bus_id=1,
        source_bus_irq=irq,
        dest_io_apic_id=io_apic.id,
        dest_io_apic_intin=0,
    )
    base_entries.append(assign_8259_to_apic)
    assign_to_apic = X86IntelMPIOIntAssignment(
        interrupt_type="INT",
        polarity="ConformPolarity",
        trigger="ConformTrigger",
        source_bus_id=1,
        source_bus_irq=irq,
        dest_io_apic_id=io_apic.id,
        dest_io_apic_intin=apicPin,
    )
    base_entries.append(assign_to_apic)
    # acpi
    assign_to_apic_acpi = X86ACPIMadtIntSourceOverride(
        bus_source=1, irq_source=irq, sys_int=apicPin, flags=0
    )
    madt_records.append(assign_to_apic_acpi)

assignISAInt(0, 2)
assignISAInt(1, 1)
for i in range(3, 15):
    assignISAInt(i, i)
workload.intel_mp_table.base_entries = base_entries
workload.intel_mp_table.ext_entries = ext_entries

madt = X86ACPIMadt(
    local_apic_address=0, records=madt_records, oem_id="madt"
)
workload.acpi_description_table_pointer.rsdt.entries.append(madt)
workload.acpi_description_table_pointer.xsdt.entries.append(madt)
workload.acpi_description_table_pointer.oem_id = "gem5"
workload.acpi_description_table_pointer.rsdt.oem_id = "gem5"
workload.acpi_description_table_pointer.xsdt.oem_id = "gem5"


# --------------------- Set up the Memory Entry ----------------------- #
# We assume below that there's at least 1MB of memory. We'll require 2
# just to avoid corner cases.
phys_mem_size = sum([r.size() for r in system.mem_ranges])
assert phys_mem_size >= 0x0_0020_0000
#assert len(system.mem_ranges) <= 2

entries = [
    X86E820Entry(addr=0x0_0000_0000, size="639kB", range_type=1),
    X86E820Entry(addr=0x0_0009_FC00, size="385kB", range_type=2),
    X86E820Entry(
        addr=0x0_0010_0000,
        size="%dB" % (hmc_size - 0x0_0010_0000),
        range_type=1,
    )
]

entry_addr = hmc_size
while entry_addr < 0x0_C000_0000:
    entries.append(
        X86E820Entry(addr=entry_addr, size="512MB", range_type=1)
    )
    entry_addr += hmc_size

# IO devices to be mapped to [0xC0000000, 0xFFFF0000). Requests to this
# specific range can pass though bridge to iobus.

# Reserve the last 16kB of the 32-bit address space for the m5op interface
entries.append(X86E820Entry(addr=0x0_FFFF_0000, size="64kB", range_type=2))

# In case the physical memory is greater than 3GB, we split it into two
# parts and add a separate e820 entry for the second part.  This entry
# starts at 0x100000000,  which is the first address after the space
# reserved for devices.
end_addr = hmc_size * args.num_mems
entry_addr = 0x1_0000_0000
while entry_addr < end_addr:
    entries.append(
        X86E820Entry(addr=entry_addr, size="512MB", range_type=1)
    )
    entry_addr += hmc_size

system.workload.e820_table.entries = entries


cmdline = "earlyprintk=ttyS0 console=ttyS0 lpj=7999923 root=/dev/hda1"
system.workload.command_line = fillInCmdline(mdesc, cmdline)


# ---------------------------- Default Setup --------------------------- #
# Set the cache line size for the entire system
system.cache_line_size = args.cacheline_size

# Create a top-level voltage domain
system.voltage_domain = VoltageDomain(voltage=args.sys_voltage)

# Create a source clock for the system and set the clock period
system.clk_domain = SrcClockDomain(
    clock=args.sys_clock, voltage_domain=system.voltage_domain
)

# Create a CPU voltage domain
system.cpu_voltage_domain = VoltageDomain()

# Create a source clock for the CPUs and set the clock period
system.cpu_clk_domain = SrcClockDomain(
    clock=args.cpu_clock, voltage_domain=system.cpu_voltage_domain
)

if args.kernel is not None:
    system.workload.object_file = args.kernel

if args.script is not None:
    system.readfile = args.script

system.init_param = args.init_param

# For now, assign all the CPUs to the same clock domain
system.cpu = [
    CPUClass(clk_domain=system.cpu_clk_domain, cpu_id=i)
    for i in range(args.num_cpus)
]


# Ruby.create_system(args, True, system, system.iobus, system._dma_ports, bootmem)
# ---------------------------- Ruby Configuration --------------------------- #
system.ruby = RubySystem()

# Generate pseudo filesystem
FileSystemConfig.config_filesystem(system, args)

# Create the network object
NetworkClass = GarnetNetwork()
IntLinkClass = GarnetIntLink()
ExtLinkClass = GarnetExtLink()
RouterClass = GarnetRouter()
InterfaceClass = GarnetNetworkInterface()
# Instantiate the network object
# so that the controllers can connect to it.
network = NetworkClass(
    ruby_system=system.ruby,
    topology=args.topology,
    routers=[],
    ext_links=[],
    int_links=[],
    netifs=[],
)

(
    network,
    IntLinkClass,
    ExtLinkClass,
    RouterClass,
    InterfaceClass,
) = Network.create_network(args, system.ruby)
system.ruby.network = network

cpus = system.cpu

protocol = buildEnv["PROTOCOL"]
exec("from ruby import %s" % protocol)
try:
    (cpu_sequencers, dir_cntrls, topology) = eval(
        "%s.create_system(args,\
                          True,\
                          system,\
                          system._dma_ports,\
                          None,\
                          system.ruby,\
                          cpus)"
        % protocol
    )
except:
    print("Error: could not create sytem for ruby protocol %s" % protocol)
    raise

# Create the network topology
topology.makeTopology(args, network, IntLinkClass, ExtLinkClass, RouterClass)


# Initialize network based on topology
Network.init_network(args, network, InterfaceClass)

# Create a port proxy for connecting the system port. This is
# independent of the protocol and kept in the protocol-agnostic
# part (i.e. here).
sys_port_proxy = RubyPortProxy(ruby_system=system.ruby)
if system.iobus is not None:
    sys_port_proxy.pio_request_port = system.iobus.cpu_side_ports

# Give the system port proxy a SimObject parent without creating a
# full-fledged controller
system.sys_port_proxy = sys_port_proxy

# Connect the system port for loading of binaries etc
system.system_port = system.sys_port_proxy.in_ports

# --------------------- Memory Controller Setup ----------------------- #
'''
if args.numa_high_bit:
    block_size_bits = args.numa_high_bit + 1 - int(math.log(args.num_dirs, 2))
    system.ruby.block_size_bytes = 2 ** (block_size_bits)
else:
    system.ruby.block_size_bytes = args.cacheline_size

system.ruby.memory_size_bits = 48  # 256TB

if args.numa_high_bit:
    dir_bits = int(math.log(args.num_dirs, 2))
    intlv_size = 2 ** (args.numa_high_bit - dir_bits + 1)
else:
    # if the numa_bit is not specified, set the directory bits as the
    # lowest bits above the block offset bits
    intlv_size = args.cacheline_size


opt_xor_low_bit = getattr(args, "xor_low_bit", 0)
#print("xor_low_bit: %d" % opt_xor_low_bit)
'''

# --------------- HMC --------------- #
for idx, dir_cntrl in enumerate(dir_cntrls):

    # create HMC host controller
    hmc_host = SubSystem()

    # Create additional crossbar
    clk = "100GHz"
    vd = VoltageDomain(voltage="1V")
    membus = NoncoherentXBar(width=8)
    #membus.badaddr_responder = BadAddr()
    #membus.default = membus.badaddr_responder.pio
    membus.width = 8
    membus.frontend_latency = 3
    membus.forward_latency = 4
    membus.response_latency = 2
    membus.clk_domain = SrcClockDomain(clock=clk, voltage_domain=vd)

    sl = [
        SerialLink(
            ranges=sl_ranges[idx * args.num_serial_links + i],
            req_size=args.link_buffer_size_req,
            resp_size=args.link_buffer_size_rsp,
            num_lanes=args.num_lanes_per_link,
            link_speed=args.serial_link_speed,
            delay=args.total_ctrl_latency,
        )
        for i in range(args.num_serial_links)
    ]
    hmc_host.seriallink = sl

    # set the clock frequency for serial link
    for i in range(args.num_serial_links):
        clk = args.link_controller_frequency
        vd = VoltageDomain(voltage="1V")
        scd = SrcClockDomain(clock=clk, voltage_domain=vd)
        hmc_host.seriallink[i].clk_domain = scd

    for i in range(args.num_links_controllers):
        membus.mem_side_ports = hmc_host.seriallink[i].cpu_side_port

    membus.cpu_side_ports = dir_cntrl.memory_out_port
    
    exec("system.membus%d = membus" % idx)


    hmc_dev = SubSystem()

    # 4 HMC Crossbars located in its logic-base (LoB)
    xb = [
        NoncoherentXBar(
            width=args.xbar_width,
            frontend_latency=args.xbar_frontend_latency,
            forward_latency=args.xbar_forward_latency,
            response_latency=args.xbar_response_latency,
        )
        for i in range(args.number_mem_crossbar)
    ]
    hmc_dev.xbar = xb

    # Attach 4 serial link to 4 crossbar/s
    for i in range(args.num_serial_links):
        hmc_host.seriallink[i].mem_side_port = hmc_dev.xbar[i].cpu_side_ports


    dir_ranges = []
    mem_ctrls = []
    
    for i in range(args.hmc_dev_num_vaults): # i = 0..15

        # Create the DRAM interface (create_mem_intf)
        dram_intf = MemClass()

        dram_intf.range = vault_ranges[idx * args.hmc_dev_num_vaults + i]

        # Enable low-power DRAM states if option is set
        dram_intf.enable_dram_powerdown = None

        # Create the controller that will drive the interface
        mem_ctrl = dram_intf.controller()
        mem_ctrls.append(mem_ctrl)

        dir_ranges.append(dram_intf.range)

        # Connect the controllers to the membus
        mem_ctrl.port = hmc_dev.xbar[i // 4].mem_side_ports
        # Set memory device size. There is an independent controller
        # for each vault. All vaults are same size.
        mem_ctrl.dram.device_size = args.hmc_dev_vault_size
    
    dir_cntrl.addr_ranges = dir_ranges
    hmc_dev.mem_ctrl = mem_ctrls

    exec("system.hmc_host%d = hmc_host" % idx)
    exec("system.hmc_dev%d = hmc_dev" % idx)
    


# Connect the cpu sequencers and the piobus
if system.iobus != None:
    for cpu_seq in cpu_sequencers:
        cpu_seq.connectIOPorts(system.iobus)

system.ruby.number_of_virtual_networks = (
    system.ruby.network.number_of_virtual_networks
)
system.ruby._cpu_ports = cpu_sequencers
system.ruby.num_of_sequencers = len(cpu_sequencers)

# Create a backing copy of physical memory in case required
if args.access_backing_store:
    system.ruby.access_backing_store = True
    system.ruby.phys_mem = SimpleMemory(
        range=system.mem_ranges[0], in_addr_map=False
    )


# Create a seperate clock domain for Ruby
system.ruby.clk_domain = SrcClockDomain(
    clock=args.ruby_clock, voltage_domain=system.voltage_domain
)

# Connect the ruby io port to the PIO bus,
# assuming that there is just one such port.
system.iobus.mem_side_ports = system.ruby._io_port.in_ports
for (i, cpu) in enumerate(system.cpu):
    #
    # Tie the cpu ports to the correct ruby system ports
    #
    cpu.clk_domain = system.cpu_clk_domain
    cpu.createThreads()
    cpu.createInterruptController()
    system.ruby._cpu_ports[i].connectCpuPorts(cpu)

# <-- Ruby config


if ObjectList.is_kvm_cpu(CPUClass) or ObjectList.is_kvm_cpu(FutureClass):
    # Assign KVM CPUs to their own event queues / threads. This
    # has to be done after creating caches and other child objects
    # since these mustn't inherit the CPU event queue.
    for i, cpu in enumerate(system.cpu):
        # Child objects usually inherit the parent's event
        # queue. Override that and use the same event queue for
        # all devices.
        for obj in cpu.descendants():
            obj.eventq_index = 0
        cpu.eventq_index = i + 1
    system.kvm_vm = KvmVM()

if args.dist:
    # This system is part of a dist-gem5 simulation
    root = makeDistRoot(
        system,
        args.dist_rank,
        args.dist_size,
        args.dist_server_name,
        args.dist_server_port,
        args.dist_sync_repeat,
        args.dist_sync_start,
        args.ethernet_linkspeed,
        args.ethernet_linkdelay,
        args.etherdump,
    )
else:
    root = Root(full_system=True, system=system)


if ObjectList.is_kvm_cpu(CPUClass) or ObjectList.is_kvm_cpu(FutureClass):
    # Required for running kvm on multiple host cores.
    # Uses gem5's parallel event queue feature
    # Note: The simulator is quite picky about this number!
    root.sim_quantum = int(1e9)  # 1 ms

if args.timesync:
    root.time_sync_enable = True

if args.frame_capture:
    VncServer.frame_capture = True

if args.wait_gdb:
    system.workload.wait_for_remote_gdb = True

Simulation.setWorkCountOptions(system, args)
Simulation.run(args, root, system, FutureClass)
