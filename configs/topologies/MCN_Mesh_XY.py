# DMN.py
# Author: Masashi Oda <oda@lab3.kuis.kyoto-u.ac.jp>

from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from topologies.BaseTopology import SimpleTopology

# Creates a generic Mesh assuming an equal number of cache
# and directory controllers.
# XY routing is enforced (using link weights)
# to guarantee deadlock freedom.


class MCN_Mesh_XY(SimpleTopology):
    description = "MCN_Mesh_XY"

    def __init__(self, controllers):
        self.nodes = controllers

    # Makes a generic mesh
    # assuming an equal number of cache and directory cntrls

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        num_nodes = options.num_cpus
        num_rows = options.mesh_rows
        assert num_rows > 0 and num_rows <= num_nodes, "mesh_rows: invalid"
        num_columns = int(num_nodes / num_rows)

        link_latency = options.link_latency  # used by simple and garnet
        router_latency = options.router_latency  # only used by garnet

        cpu_nodes = []
        l2c_nodes = []
        dir_nodes = []
        dma_nodes = []
        for node in nodes:
            if node.type == "L1Cache_Controller":
                cpu_nodes.append(node)
            elif node.type == "L2Cache_Controller":
                l2c_nodes.append(node)
            elif node.type == "Directory_Controller":
                dir_nodes.append(node)
            elif node.type == "DMA_Controller":
                dma_nodes.append(node)
        assert len(cpu_nodes) == 4, "num_cpus: invalid"
        assert len(l2c_nodes) == 4, "num_l2caches: invalid"
        assert len(dir_nodes) == options.num_dirs, "num_dir: invalid"

        # Create the routers in the mesh
        routers = [
            Router(router_id=i, latency=router_latency) for i in range(num_nodes + 4)
        ]
        network.routers = routers

        # link counter to set unique link ids
        link_count = 0

        ext_links = []

        proc = [num_nodes, num_nodes+1, num_nodes+2, num_nodes+3]
        mem = list(range(num_nodes))

        # Connect each CPU to the appropriate router
        for (i, n) in enumerate(cpu_nodes):
            ext_links.append(
                ExtLink(
                    link_id=link_count,
                    ext_node=n,
                    int_node=routers[proc[i]],
                    latency=link_latency,
                )
            )
            link_count += 1
        # Connect each L2 cache bank to the appropriate router
        for (i, n) in enumerate(l2c_nodes):
            ext_links.append(
                ExtLink(
                    link_id=link_count,
                    ext_node=n,
                    int_node=routers[proc[i]],
                    latency=link_latency,
                )
            )
            link_count += 1
        # Connect each directory controller to the appropriate router
        for (i, n) in enumerate(dir_nodes):
            ext_links.append(
                ExtLink(
                    link_id=link_count,
                    ext_node=n,
                    int_node=routers[mem[i]],
                    latency=link_latency,
                )
            )
            link_count += 1
        # Connect the DMA nodes to router 0. These should only be DMA nodes.
        for (i, n) in enumerate(dma_nodes):
            assert node.type == "DMA_Controller"
            ext_links.append(
                ExtLink(
                    link_id=link_count,
                    ext_node=n,
                    int_node=routers[0],
                    latency=link_latency,
                )
            )
            link_count += 1

        network.ext_links = ext_links

        # Create the dragonfly links.
        int_links = []

        # East output to West input links (weight = 1)
        for row in range(num_rows):
            for col in range(num_columns):
                if col + 1 < num_columns:
                    east_out = col + (row * num_columns)
                    west_in = (col + 1) + (row * num_columns)
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[mem[east_out]],
                            dst_node=routers[mem[west_in]],
                            src_outport="East",
                            dst_inport="West",
                            latency=link_latency,
                            weight=1,
                        )
                    )
                    link_count += 1

        # West output to East input links (weight = 1)
        for row in range(num_rows):
            for col in range(num_columns):
                if col + 1 < num_columns:
                    east_in = col + (row * num_columns)
                    west_out = (col + 1) + (row * num_columns)
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[mem[west_out]],
                            dst_node=routers[mem[east_in]],
                            src_outport="West",
                            dst_inport="East",
                            latency=link_latency,
                            weight=1,
                        )
                    )
                    link_count += 1

        # North output to South input links (weight = 2)
        for col in range(num_columns):
            for row in range(num_rows):
                if row + 1 < num_rows:
                    north_out = col + (row * num_columns)
                    south_in = col + ((row + 1) * num_columns)
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[mem[north_out]],
                            dst_node=routers[mem[south_in]],
                            src_outport="North",
                            dst_inport="South",
                            latency=link_latency,
                            weight=2,
                        )
                    )
                    link_count += 1

        # South output to North input links (weight = 2)
        for col in range(num_columns):
            for row in range(num_rows):
                if row + 1 < num_rows:
                    north_in = col + (row * num_columns)
                    south_out = col + ((row + 1) * num_columns)
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[mem[south_out]],
                            dst_node=routers[mem[north_in]],
                            src_outport="South",
                            dst_inport="North",
                            latency=link_latency,
                            weight=2,
                        )
                    )
                    link_count += 1

        # Memory output to 
        mem_corner = [0, num_columns-1, num_nodes-num_columns, num_nodes-1]
        for i, p in enumerate(proc):
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[p],
                    dst_node=routers[mem_corner[i]],
                    src_outport="Processor",
                    dst_inport="Memory",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[mem_corner[i]],
                    dst_node=routers[p],
                    src_outport="Memory",
                    dst_inport="Processor",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1

        network.int_links = int_links

    # Register nodes with filesystem
    def registerTopology(self, options):
        for i in range(options.num_cpus):
            FileSystemConfig.register_node(
                [i], MemorySize(options.mem_size) // options.num_cpus, i
            )
