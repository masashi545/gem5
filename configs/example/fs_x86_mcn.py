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
from common import CacheConfig
from common import CpuConfig
from common import MemConfig
from common import ObjectList
from common.Caches import *
from common import Options
from common import FileSystemConfig

from topologies import *
from network import Network

# ----------------------------- Add Options ---------------------------- #
parser = argparse.ArgumentParser()
Options.addCommonOptions(parser)
Options.addFSOptions(parser)
Ruby.define_options(parser)

# ---------------------------- Parse Options --------------------------- #
args = parser.parse_args()

# CPU and Memory
(CPUClass, mem_mode, FutureClass) = Simulation.setCPUClass(args)
MemClass = Simulation.setMemClass(args)

# ---------------------------- Setup System ---------------------------- #
system = System()
# System -> src/sim/System.py

mdesc = SysConfig(
    disks=args.disk_image,
    rootdev=args.root_device,
    mem=args.mem_size,
    os_type=args.os_type,
)
system.readfile = mdesc.script()

system.mem_mode = mem_mode

system.workload = X86FsLinux()
# X86FsLinux -> src/arch/x86/X88FsWorkload.py

system.m5op_base = 0xFFFF0000
system.mem_range = [AddrRange(start=0x80000000, size=mdesc.mem())]

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
system.pc.south_bridge.ide.disks = makeCowDisks(mdesc.disks())

# Add in a Bios information structure.
system.workload.smbios_table.structures = [X86SMBiosBiosInformation()]
# X86SMBiosBiosInformation -> src/arch/x86/bios/SMBios.py

# --------------------- Set up the Intel MP table ----------------------- #
base_entries = []
ext_entries = []
madt_records = []
for i in range(args.num_cpus):
    base_entries.append(
        X86IntelMPProcessor(
            local_apic_id=i,
            local_apic_version=0x14,
            enable=True,
            bootstrap=(i == 0),
        )
    )
    madt_records.append(
        X86ACPIMadtLAPIC(acpi_processor_id=i, apic_id=i, flags=1)
    )

io_apic = X86IntelMPIOAPIC(
    id=args.num_cpus, version=0x11, enable=True, address=0xFEC00000
)
system.pc.south_bridge.io_apic.apic_id = io_apic.id

base_entries.append(io_apic)

madt_records.append(
    X86ACPIMadtIOAPIC(id=io_apic.id, address=io_apic.address, int_base=0)
)

base_entries.append(X86IntelMPBus(bus_id=0, bus_type="PCI"))
base_entries.append(X86IntelMPBus(bus_id=1, bus_type="ISA"))

ext_entries.append(
    X86IntelMPBusHierarchy(bus_id=1, subtractive_decode=True, parent_bus=0)
)

base_entries.append(
    X86IntelMPIOIntAssignment(
        interrupt_type="INT",
        polarity="ConformPolarity",
        trigger="ConformTrigger",
        source_bus_id=0,
        source_bus_irq=0 + (4 << 2),
        dest_io_apic_id=io_apic.id,
        dest_io_apic_intin=16,
    )
)

madt_records.append(
    X86ACPIMadtIntSourceOverride(
        bus_source=pci_dev4_inta.source_bus_id,
        irq_source=pci_dev4_inta.source_bus_irq,
        sys_int=pci_dev4_inta.dest_io_apic_intin,
        flags=0,
    )
)

def assignISAInt(irq, apicPin):
    base_entries.append(
        X86IntelMPIOIntAssignment(
            interrupt_type="ExtInt",
            polarity="ConformPolarity",
            trigger="ConformTrigger",
            source_bus_id=1,
            source_bus_irq=irq,
            dest_io_apic_id=io_apic.id,
            dest_io_apic_intin=0,
        )
    )

    base_entries.append(
        X86IntelMPIOIntAssignment(
            interrupt_type="INT",
            polarity="ConformPolarity",
            trigger="ConformTrigger",
            source_bus_id=1,
            source_bus_irq=irq,
            dest_io_apic_id=io_apic.id,
            dest_io_apic_intin=apicPin,
        )
    )
    # acpi
    madt_records.append(
        X86ACPIMadtIntSourceOverride(
            bus_source=1, irq_source=irq, sys_int=apicPin, flags=0
        )
    )


assignISAInt(0, 2)
assignISAInt(1, 1)
for i in range(3, 15):
    assignISAInt(i, i)

system.workload.intel_mp_table.base_entries = base_entries
system.workload.intel_mp_table.ext_entries = ext_entries

madt = X86ACPIMadt(local_apic_address=0, records=madt_records, oem_id="madt")
system.workload.acpi_description_table_pointer.rsdt.entries.append(madt)
system.workload.acpi_description_table_pointer.xsdt.entries.append(madt)

system.workload.acpi_description_table_pointer.oem_id = "gem5"
system.workload.acpi_description_table_pointer.rsdt.oem_id = "gem5"
system.workload.acpi_description_table_pointer.xsdt.oem_id = "gem5"


# --------------------- Set up the Memory Entry ----------------------- #
entries = [  # Mark the first megabyte of memory as reserved
    X86E820Entry(addr=0x0000_0000, size="639kB", range_type=1),
    X86E820Entry(addr=0x0009_FC00, size="385kB", range_type=2),
    # Mark the rest of physical memory as available
    X86E820Entry(
        addr=0x0010_0000,
        size="%dB" % (system.mem_ranges[0].size() - 0x0010_0000),
        range_type=1,
    ),
]

# Reserve the last 16kB of the 32-bit address space for the m5op interface
entries.append(X86E820Entry(addr=0xFFFF_0000, size="64kB", range_type=2))

# In case the physical memory is greater than 3GB, we split it into two
# parts and add a separate e820 entry for the second part.  This entry
# starts at 0x100000000,  which is the first address after the space
# reserved for devices.
if len(system.mem_ranges) == 2:
    entries.append(
        X86E820Entry(
            addr=0x1_0000_0000,
            size="%dB" % (system.mem_ranges[1].size()),
            range_type=1,
        )
    )

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
exec("from . import %s" % protocol)
try:
    (cpu_sequencers, dir_cntrls, topology) = eval(
        "%s.create_system(args, \
                          full_system, \
                          system, \
                          dma_ports, \
                          bootmem, \
                          system.ruby, \
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

setup_memory_controllers(system, system.ruby, dir_cntrls, args)

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


if ObjectList.is_kvm_cpu(TestCPUClass) or ObjectList.is_kvm_cpu(FutureClass):
    # Required for running kvm on multiple host cores.
    # Uses gem5's parallel event queue feature
    # Note: The simulator is quite picky about this number!
    root.sim_quantum = int(1e9)  # 1 ms

if args.timesync:
    root.time_sync_enable = True

if args.frame_capture:
    VncServer.frame_capture = True

if (
    buildEnv["TARGET_ISA"] == "arm"
    and not args.bare_metal
    and not args.dtb_filename
):
    if args.machine_type not in [
        "VExpress_GEM5",
        "VExpress_GEM5_V1",
        "VExpress_GEM5_V2",
        "VExpress_GEM5_Foundation",
    ]:
        warn(
            "Can only correctly generate a dtb for VExpress_GEM5_* "
            "platforms, unless custom hardware models have been equipped "
            "with generation functionality."
        )

    # Generate a Device Tree
    for sysname in ("system", "testsys", "drivesys"):
        if hasattr(root, sysname):
            sys = getattr(root, sysname)
            sys.workload.dtb_filename = os.path.join(
                m5.options.outdir, "%s.dtb" % sysname
            )
            sys.generateDtb(sys.workload.dtb_filename)

if args.wait_gdb:
    system.workload.wait_for_remote_gdb = True

Simulation.setWorkCountOptions(system, args)
Simulation.run(args, root, system, FutureClass)
