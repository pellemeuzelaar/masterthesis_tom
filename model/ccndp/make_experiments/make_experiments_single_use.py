"""
Makes the random instances used in the numerical experiments section of the
paper. See there for details.
"""

from itertools import product
import pandas as pd
import numpy as np
import geopy.distance

from ccndp.classes import Edge
from ccndp.classes import FacilityNode as Facility
from ccndp.classes import ProblemData, Resource
from ccndp.classes import SinkNode as Sink
from ccndp.classes import SourceNode as Source
from ccndp.classes import StorageNode as Storage
from ccndp.functions import pairwise

# DEMAND, NEEDS, CAPACITY

def make_experiment():
    resources = [Resource(0, "CO2"), Resource(1, "Urea"), Resource(2, "E-methanol"), Resource(3, "SAF")]

    # Supply node data and correct the scale of quantity, which is now in kg and needs to be tonne
    emitters = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/AllEmittersNW(kg:y).csv")
    emitters = pd.DataFrame(emitters)

    # Facility node data
    conversion = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Facilities/NW/NW_FINAL_ALL_USES.csv")
    conversion = pd.DataFrame(conversion)

    # Demand node data
    consumption = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Demand/NW/Demand_NW_ALL_USES.csv")
    consumption = pd.DataFrame(consumption)

    # Storage node data
    storage = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Storage/Storage_NW_2.csv")
    storage = pd.DataFrame(storage)

    # The values inputted for different nodes imported from dataframe
    supply = emitters.iloc[:,4:].values/1000 # Is in kg Convert to ton
    demand = consumption.iloc[:,5:].values*1000 # Is in Kt, so convert to ton
    stored = storage.iloc[:,7:].values*1000000 # Is in Mt, so convert to ton

    # Source node input values, facilities, and sinks, and what they make and need.
    source_locs = emitters[["Latitude", "Longitude"]].to_numpy()
    num_sources = len(emitters.index)
    src_idcs = emitters.index.values
    src_makes = [(resources[0]) for _ in range(num_sources)] # Always makes CO2 in our case, so 0
    sources = list(map(Source, src_idcs, source_locs, src_makes, supply))
    print("total emissions at ALL (possible) source nodes is: ", sum(supply), "t")

    # Facility node input values
    num_facs = len(conversion.index)
    fac_makes = []
    fac_locs = conversion[["Latitude", "Longitude"]].to_numpy()
    fac_idcs = conversion.index.values + num_sources
    for i in range (num_facs):
        if conversion["Product"][i] == "Urea":
            fac_makes.append(resources[1])
        if conversion["Product"][i] == "Methanol":
            fac_makes.append(resources[2])
        if conversion["Product"][i] == "SAF":
            fac_makes.append(resources[3])

    fac_needs = [(resources[:1]) for _ in range(num_facs)] # Always needs CO2 in our case
    facilities = list(map(Facility, fac_idcs, fac_locs, fac_makes, fac_needs))

    # Sink node input values
    sink_idcs = consumption.index.values + num_sources + num_facs
    sink_locs = consumption[["Latitude", "Longitude"]].to_numpy()
    num_sinks = len(consumption.index)

    # Demands for different uses
    # urea_demand = []
    # methanol_demand = []
    # saf_demand = []
    #
    # for i in range(num_sinks):
    #     if consumption["Product"][i] == "Urea":
    #         urea_demand.append(consumption["Demand (Kton/year)"][i])
    #     if consumption["Product"][i] == "Methanol":
    #         methanol_demand.append(consumption["Demand (Kton/year)"][i])
    #     if consumption["Product"][i] == "SAF":
    #         saf_demand.append(consumption["Demand (Kton/year)"][i])

    sink_needs = []
    for i in range (num_sinks):
        if consumption["Product"][i] == "Urea":
            sink_needs.append(resources[1])
        if consumption["Product"][i] == "Methanol":
            sink_needs.append(resources[2])
        if consumption["Product"][i] == "SAF":
            sink_needs.append(resources[3])

    sinks = list(map(Sink, sink_idcs, sink_locs, sink_needs, demand))
    print("Yearly capacity of demand at sink nodes is: ", sum(demand), "t")

    # Storage node input values
    storages_locs = storage[["Latitude", "Longitude"]].to_numpy()
    storages_idcs = storage.index.values + num_sources + num_facs + num_sinks
    num_storages = len(storage.index)
    storage_needs = [resources[0] for _ in range(num_storages)]
    storages = list(map(Storage, storages_idcs, storages_locs, storage_needs, stored))
    print("Yearly capacity of storage at storage nodes is: ", sum(stored), "t")

    # Total nodes that will be converted to json
    nodes = sources + facilities + sinks + storages


    # Edges. First we construct all source and facility edges. These
    # represent the construction decisions at the nodes.
    edges = []

    for src in sources:
        # Capacity for source emissions
        capacity = supply[src.idx] # If model decides on multiple edges from 1 source this will
        # result in greater capacity on the edge than on the source node

        # Capture costs, different per industry
        cost_per_ton = []
        cost_per_ton_Fertilizers = 25.95
        cost_per_ton_Cement = 95.79
        cost_per_ton_Refineries = 16.61
        cost_per_ton_Power_Station = 79.02
        cost_per_ton_Iron_and_Steel = 99.97
        cost_per_ton_Waste = 25.95

        # Append costs to dataframe for each industry
        for i in range(num_sources):
            if emitters["Industry"][i] == "F":
                cost_per_ton.append(cost_per_ton_Fertilizers)
            if emitters["Industry"][i] == "C":
                cost_per_ton.append(cost_per_ton_Cement)
            if emitters["Industry"][i] == "R":
                cost_per_ton.append(cost_per_ton_Refineries)
            if emitters["Industry"][i] == "PS":
                cost_per_ton.append(cost_per_ton_Power_Station)
            if emitters["Industry"][i] == "IS":
                cost_per_ton.append(cost_per_ton_Iron_and_Steel)
            if emitters["Industry"][i]=="D":
                cost_per_ton.append(cost_per_ton_Waste)

        # Make edge variable from costs to append to edges
        cost = cost_per_ton[src.idx]

        # Append costs to the edges
        edges.append(Edge(src, src, cost, capacity, "B"))

    for fac in facilities:
        # Conversion costs in euro per tonne CO2 for each end-use
        conversion_cost_per_ton = []
        cost_per_ton_urea = 458.47 # is in euro per ton
        cost_per_ton_methanol = 700.63
        cost_per_ton_saf = 190.00

        for i in range(num_facs):
            if conversion["Product"][i] == "Urea":
                conversion_cost_per_ton.append(cost_per_ton_urea)
            if conversion["Product"][i] == "Methanol":
                conversion_cost_per_ton.append(cost_per_ton_methanol)
            if conversion["Product"][i] == "SAF":
                conversion_cost_per_ton.append(cost_per_ton_saf)

        # Make edge variable for conversion costs
        cost = conversion_cost_per_ton[fac.idx-num_sources]

        capacity_urea_plants = 178590 #0.17859*1000000 # is in Mton, converted to ton
        capacity_methanol_plants = 72660 #0.07266*1000000
        capacity_saf_plants = 324940 #0.32494*1000000

        capacity_fac = []
        for i in range(num_facs):
            if conversion["Product"][i] == "Urea":
                capacity_fac.append(capacity_urea_plants)
            if conversion["Product"][i] == "Methanol":
                capacity_fac.append(capacity_methanol_plants)
            if conversion["Product"][i] == "SAF":
                capacity_fac.append(capacity_saf_plants)

        # Capacity for each facility
        capacity = [capacity_fac[fac.idx-num_sources]]

        # Append vars to edges
        edges.append(Edge(fac, fac, cost, capacity, "B"))

    for strg in storages:

        cost_DOGF_onshore = 1.0 # is in euro per ton
        cost_DOGF_offshore = 6.4
        cost_SA_onshore = 9.4
        cost_SA_offshore = 30.1

        cost_strg = []
        for i in range(num_storages):
            if storage["Offshore or Onshore"][i] == "Onshore":
                if storage["SA or DOGF"][i] == "DOGF":
                    cost_strg.append(cost_DOGF_onshore)
            if storage["Offshore or Onshore"][i] == "Offshore":
                if storage["SA or DOGF"][i] == "DOGF":
                    cost_strg.append(cost_DOGF_offshore)
            if storage["Offshore or Onshore"][i] == "Onshore":
                if storage["SA or DOGF"][i] == "SA":
                    cost_strg.append(cost_SA_onshore)
            if storage["Offshore or Onshore"][i] == "Offshore":
                if storage["SA or DOGF"][i] == "SA":
                    cost_strg.append(cost_SA_offshore)

        counter = num_sinks + num_facs + num_sources
        cost = [cost_strg[strg.idx-counter]]
        capacity = [3520000] # 3.52 Mton, converted to ton

        # Append to edges
        edges.append(Edge(strg, strg, cost, capacity, "B"))

    # All edges BETWEEN source and fac nodes (not self nodes)
    for inlayer, outlayer in pairwise([sources, facilities]):
        sumlist = []
        for frm, to in product(inlayer, outlayer):
            capacity = frm.supply # Same as supply at source node, not more than the pipeline capacity of 3.5MT
            sumlist.append(capacity)
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost_capital = (24.7 * (3.1556926**0.35) * (distance**1.13))/3.1556926 # this unit ist just a per km cost
            cost_OM  = 0.02 * cost_capital # Opex per Mton as percentage (2%)
            cost = cost_capital + cost_OM
            edges.append(Edge(frm, to, cost, capacity, "C"))
    print("capacity of CO2 flows along edges going from sources to facilities is: ", sum(sumlist), "t")

    # All edges BETWEEN fac and sink nodes (not self nodes)
    for inlayer, outlayer in pairwise([facilities, sinks]):
        sumlist = []
        for frm, to in product(inlayer, outlayer):
            capacity = to.demand # Same as supply at fac node, which is total demand at the sink node
            sumlist.append(capacity)
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost = (0.1*distance) #  cost is 0.1eur/t per ton
            edges.append(Edge(frm, to, cost, capacity, "C"))
    print("capacity of end-use demand along edges going from facilities to sinks is: ", sum(sumlist), "t")

    #All edges BETWEEN source and storage nodes (not self nodes)
    for inlayer, outlayer in pairwise([sources, storages]):
        sumlist = []
        for frm, to in product(inlayer, outlayer):
            capacity = to.storage # Demand at the storage node, i.e. 3.52Mton
            sumlist.append(capacity)
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost_capital = (24.7 * (3.1556926**0.35) * (distance**1.13))/3.1556926
            cost_OM  = 0.02 * cost_capital # Opex per Mton
            cost = cost_capital + cost_OM
            edges.append(Edge(frm, to, cost, capacity, "C"))
    print("capacity of CO2 flow along edges going from sources to storage edges is: ", sum(sumlist), "t")

    # Put all data into file
    data = ProblemData(
        resources=resources, nodes=nodes, edges=edges, num_scenarios=int(1)
    )
    return data

def main():
    data = make_experiment()
    data.to_file("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Instances/FINAL_1.json")

if __name__ == "__main__":
    main()
