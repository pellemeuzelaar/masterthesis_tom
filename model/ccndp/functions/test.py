from ccndp.classes import (
    ProblemData,
    SourceNode,
    StorageNode,
    SinkNode,
    FacilityNode,
    Resource,
    Edge,
)

def main():
    # Graph looks like this:
    #           / fac1 \
    # source0 -         - fac3 -- sink4
    #           \ fac2 /
    resources = [Resource(0, "CO2"), Resource(1, "urea"), Resource(2, "methanol")]
    nodes = [ # look like: idx, coords, makes/needs, capacity
        SourceNode(0, (0, 1), resources[0], [10]),
        SourceNode(1, (0, 2), resources[0], [10]),
        SourceNode(2, (0, 3), resources[0], [10]),
        FacilityNode(3, (1, -2), resources[1], resources[:1]),
        FacilityNode(4, (1, -4), resources[1], resources[:1]),
        FacilityNode(5, (1, -3), resources[1], resources[:1]),
        StorageNode(6, (2, 0), resources[0], [1]),
        StorageNode(7, (2, 1), resources[0], [1]),
        SinkNode(8, (2, 2), resources[1], [1]),
    ]
    edges = [ #look like: from, to, cost, capacity
        Edge(nodes[0], nodes[0], 1.0, [10.0], "C"),  # src
        Edge(nodes[0], nodes[3], 1.0, [1.0], "C"),  #
        Edge(nodes[0], nodes[4], 1.0, [1.0], "C"),  #
        Edge(nodes[0], nodes[5], 1.0, [1.0], "C"),  #
        Edge(nodes[0], nodes[6], 1.0, [1.0], "C"),  #
        Edge(nodes[0], nodes[7], 1.0, [1.0], "C"),  #

        Edge(nodes[1], nodes[1], 1.0, [10.0], "C"),  # src
        Edge(nodes[1], nodes[3], 1.0, [1.0], "C"),  #
        Edge(nodes[1], nodes[4], 1.0, [1.0], "C"),  #
        Edge(nodes[1], nodes[5], 1.0, [1.0], "C"),  #
        Edge(nodes[1], nodes[6], 1.0, [1.0], "C"),  #
        Edge(nodes[1], nodes[7], 1.0, [1.0], "C"),  #

        Edge(nodes[2], nodes[2], 1.0, [10.0], "C"),  # src
        Edge(nodes[2], nodes[3], 1.0, [1.0], "C"),  #
        Edge(nodes[2], nodes[4], 1.0, [1.0], "C"),  #
        Edge(nodes[2], nodes[5], 1.0, [1.0], "C"),  #
        Edge(nodes[2], nodes[6], 1.0, [1.0], "C"),  #
        Edge(nodes[2], nodes[7], 1.0, [1.0], "C"),  #

        Edge(nodes[3], nodes[3], 1.0, [1.0], "C"),  # (src, fac1)
        Edge(nodes[4], nodes[4], 1.0, [1.0], "C"),  # (src, fac1)
        Edge(nodes[5], nodes[5], 1.0, [1.0], "C"),  # (src, fac1)

        Edge(nodes[3], nodes[8], 1.0, [1.0], "C"),  # (src, fac1)
        Edge(nodes[4], nodes[8], 1.0, [1.0], "C"),  # fac1
        Edge(nodes[5], nodes[8], 1.0, [1.0], "C"),  # (fac1, fac3)

    ]

    data = ProblemData(nodes, edges, resources, 1)
    data.to_file("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Instances/test.json")


if __name__ == "__main__":
    main()
