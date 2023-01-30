# DragonFly.py
# Author: Masashi Oda

from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from topologies.BaseTopology import SimpleTopology

class DragonFly(SimpleTopology):
    description='DragonFly'

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        num_routers = 16
        num_rows = 4
        num_columns = 4

        link_latency = options.link_latency     # used by simple and garnet
        router_latency = options.router_latency # only used by garnet

        cpu_nodes = []
        l2c_nodes = []
        dir_nodes = []
        dma_nodes = []
        for node in nodes:
            if node.type == 'L2Cache_Controller':
                l2c_nodes.append(node)
            elif node.type == 'Directory_Controller':
                dir_nodes.append(node)
            elif node.type == 'DMA_Controller':
                dma_nodes.append(node)
        assert len(l2c_nodes) == 4, "num_l2c_nodes: invalid"
        assert len(dir_nodes) == 12, "num_dir_nodes: invalid"
        #assert len(dma_nodes) == 4, "num_dma_nodes: invalid"

        # Create the routers in  4x4 dragonfly
        routers = [Router(router_id=i, latency=router_latency) \
            for i in range(num_routers)]
        network.routers = routers

        # Link counter to set unique link IDs
        link_count = 0
        
        ext_links = []

        corner = [0, num_columns - 1, num_routers - num_columns, num_routers - 1]
        not_corner = list(range(num_routers))
        for i in corner:
          not_corner.remove(i)

        # Connect each L2 cache bank to the appropriate router
        for (i, n) in enumerate(l2c_nodes):
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[corner[i]],
                                    latency=link_latency))
            link_count += 1
        # Connect each directory controller to the appropriate router
        for (i, n) in enumerate(dir_nodes):
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[not_corner[i]],
                                    latency=link_latency))
            link_count += 1
        # Connect the DMA nodes to router 0. These should only be DMA nodes.
        for (i, n) in enumerate(dma_nodes):
            assert(node.type == 'DMA_Controller')
            ext_links.append(ExtLink(link_id=link_count, ext_node=n, 
                                     int_node=routers[0]))
            link_count += 1

        network.ext_links = ext_links


        # Create the dragonfly links.
        int_links = []

        # East output to West input links (weight = 1)
        for row in range(num_rows):
            for col in range(num_columns):
                if ((col + 1 < num_columns) & (col % 2 == 0)):
                    east_out = col + (row * num_columns)
                    west_in = (col + 1) + (row * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[east_out],
                                             dst_node=routers[west_in],
                                             src_outport="East",
                                             dst_inport="West",
                                             latency=link_latency,
                                             weight=1))
                    link_count += 1

        # West output to East input links (weight = 1)
        for row in range(num_rows):
            for col in range(num_columns):
                if (col + 1 < num_columns):
                    east_in = col + (row * num_columns)
                    west_out = (col + 1) + (row * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[west_out],
                                             dst_node=routers[east_in],
                                             src_outport="West",
                                             dst_inport="East",
                                             latency=link_latency,
                                             weight=1))
                    link_count += 1

        # North output to South input links (weight = 1)
        for col in range(num_columns):
            for row in range(num_rows):
                if (row + 1 < num_rows):
                    north_out = col + (row * num_columns)
                    south_in = col + ((row + 1) * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[north_out],
                                             dst_node=routers[south_in],
                                             src_outport="North",
                                             dst_inport="South",
                                             latency=link_latency,
                                             weight=1))
                    link_count += 1

        # South output to North input links (weight = 1)
        for col in range(num_columns):
            for row in range(num_rows):
                if (row + 1 < num_rows):
                    north_in = col + (row * num_columns)
                    south_out = col + ((row + 1) * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[south_out],
                                             dst_node=routers[north_in],
                                             src_outport="South",
                                             dst_inport="North",
                                             latency=link_latency,
                                             weight=1))
                    link_count += 1
       
        network.int_links = int_links


    # Register nodes with filesystem
    def registerTopology(self, options):
        for i in range(options.num_cpus):
            FileSystemConfig.register_node([i],
                    MemorySize(options.mem_size) // options.num_cpus, i)
