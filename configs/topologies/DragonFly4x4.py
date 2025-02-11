# DragonFly4x4.py
# Author: Masashi Oda <oda@lab3.kuis.kyoto-u.ac.jp>

"""
command option
    --caches \ 
    --l2cache \ 
    --ruby \ 
    --network=garnet \ 
    --topology=DragonFly4x4 \ 
    --num-cpus=4 \ 
    --num-l2caches=4 \ 
    --num-dir=4 \  
"""

from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from topologies.BaseTopology import SimpleTopology


class DragonFly4x4(SimpleTopology):
    description = "DragonFly4x4"

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        k = 4
        n = k * k
        assert n == options.num_mems, "num_mem_nodes: invalid"

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
        assert len(cpu_nodes) == 4, "num_cpu_nodes: invalid"
        assert len(l2c_nodes) == 4, "num_l2c_nodes: invalid"
        assert len(dir_nodes) == options.num_dirs, "num_dir_nodes: invalid"

        # Create the routers in  4x4 dragonfly
        routers = [
            Router(router_id=i, latency=router_latency) for i in range(n)
        ]
        network.routers = routers

        # Link counter to set unique link IDs
        link_count = 0

        ext_links = []

        corner = [0, 5, 10, 15]
        not_corner = list(range(n))
        for i in corner:
            not_corner.remove(i)

        # Connect each CPU to the appropriate router
        for (i, n) in enumerate(cpu_nodes):
            ext_links.append(
                ExtLink(
                    link_id=link_count,
                    ext_node=n,
                    int_node=routers[corner[i]],
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
                    int_node=routers[corner[i]],
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
                    int_node=routers[i],
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

        # East <-> West links (weight = 1)
        east_list = [0, 2, 4, 6, 8, 10, 12, 14, 1, 11]
        west_list = [1, 3, 5, 7, 9, 11, 13, 15, 4, 14]
        for i in range(len(east_list)):
            east = east_list[i]
            west = west_list[i]
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[east],
                    dst_node=routers[west],
                    src_outport="East",
                    dst_inport="West",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[west],
                    dst_node=routers[east],
                    src_outport="West",
                    dst_inport="East",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1

        # North <-> South links (weight = 1)
        north_list = [0, 1, 4, 5, 8, 9, 12, 13, 2, 7]
        south_list = [2, 3, 6, 7, 10, 11, 14, 15, 8, 13]
        for i in range(len(north_list)):
            north = north_list[i]
            south = south_list[i]
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[north],
                    dst_node=routers[south],
                    src_outport="North",
                    dst_inport="South",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[south],
                    dst_node=routers[north],
                    src_outport="South",
                    dst_inport="North",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1

        # North-East <-> South-West links (weight = 1)
        north_east_list = [0, 4, 8, 12, 3]
        south_west_list = [3, 7, 11, 15, 12]
        for i in range(len(north_east_list)):
            north_east = north_east_list[i]
            south_west = south_west_list[i]
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[north_east],
                    dst_node=routers[south_west],
                    src_outport="North-East",
                    dst_inport="South-West",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[south_west],
                    dst_node=routers[north_east],
                    src_outport="South-West",
                    dst_inport="North-East",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1

        # North-West <-> South-East links (weight = 1)
        north_west_list = [1, 5, 9, 13, 6]
        south_east_list = [2, 6, 10, 14, 9]
        for i in range(len(north_west_list)):
            north_west = north_west_list[i]
            south_east = south_east_list[i]
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[north_west],
                    dst_node=routers[south_east],
                    src_outport="North-West",
                    dst_inport="South-East",
                    latency=link_latency,
                    weight=1,
                )
            )
            link_count += 1
            int_links.append(
                IntLink(
                    link_id=link_count,
                    src_node=routers[south_east],
                    dst_node=routers[north_west],
                    src_outport="South-East",
                    dst_inport="North-West",
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
