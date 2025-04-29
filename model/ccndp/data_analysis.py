"""
Makes the random instances used in the numerical experiments section of the
paper. See there for details.
"""

from itertools import product
import pandas as pd
import geopy.distance

from ccndp.classes import Edge
from ccndp.classes import FacilityNode as Facility
from ccndp.classes import ProblemData, Resource
from ccndp.classes import SinkNode as Sink
from ccndp.classes import SourceNode as Source
from ccndp.classes import StorageNode as Storage
from ccndp.functions import pairwise


def make_experiment():
    resources = [Resource(0, "CO2"), Resource(1, "Urea"), Resource(2, "Methanol"), Resource(3, "SAF")]

    # Supply node data and correct the scale of quantity, which is now in kg and needs to be tonne
    emitters = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/AllEmittersNW(kg:y).csv")
    emitters.sort_values(by="TotalQuantity (kg/year)", ascending=False, inplace=True)
    print(emitters)
    # supply = emitters["TotalQuantity"] #Quantity is in tonnes per year so divide to get tonne
    # supply.sort_values()
    #
    # # Facility node data
    # conversion = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Facilities/FacilitiesSE.csv")
    #
    # # Demand node data
    # consumption = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Demand/SE.csv")
    #
    # # Storage node data
    # storage = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Storage/StorageSE.csv")
    # # Create average injection column and fill NaN values for new column and also correct the scale (mill tonne per y):
    # storage["yearly_capacity"] = (storage["min_injection_capacity"] + storage["max_injection_capacity"])/2
    # storage["yearly_capacity"] = 3.51875 # this is the mean returned by the line below
    # storage["yearly_capacity"] = storage["yearly_capacity"].fillna(storage["yearly_capacity"].mean())
    #
    # # The values inputted for different nodes imported from dataframe
    # supply = emitters.iloc[:, 4:].values/1000000 # quantity is now in tonnes, must go to million so we divide
    # demand = consumption.iloc[:, 4:].values/10000 # quantity is already in Mt
    # stored = storage.iloc[:, 6:].values # quantity is already in Mt
    #
    # # Different countries
    # emitters_RO = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/AllEmittersRO.csv")
    # emitters_BG = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/AllEmittersBUL.csv")
    # emitters_GR = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/AllEmittersGR.csv")
    #
    # emitters_NL = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Data past theses/carlos/Data/Emitters/NW/NL.csv")
    # emitters_UK = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Data past theses/carlos/Data/Emitters/NW/UK.csv")
    # emitters_DK = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Data past theses/carlos/Data/Emitters/NW/DK.csv")
    #
    # # Supply countries
    # supply_RO = emitters_RO["TotalQuantity"]/1000000 # In tonnes to Mtonnes
    # supply_BG = emitters_BG["TotalQuantity"]/1000000
    # supply_GR = emitters_GR["TotalQuantity"]/1000000
    # supply_NL = emitters_NL["TotalQuantity"]/1000000000 # In KG to MT
    # supply_UK = emitters_UK["TotalQuantity"]/1000000000
    # supply_DK = emitters_DK["TotalQuantity"]/1000000000
    #
    # print("total emissions RO", sum(supply_RO))
    # print("total emissions BUL", sum(supply_BG))
    # print("total emissions GR", sum(supply_GR))
    # print("total emissions NL", sum(supply_NL))
    # print("total emissions UK", sum(supply_UK))
    # print("total emissions DK", sum(supply_DK))
    # print("total emissions NW", sum(emitters_nw["TotalQuantity"]/1000000000))
    # print("total emissions SE", sum(emitters["TotalQuantity"]/1000000))
    #
    #
    #
    # # Source node input values, facilities, and sinks, and what they make and need.
    # source_locs = emitters[["Latitude", "Longitude"]].to_numpy()
    # num_sources = len(emitters.index)
    # src_idcs = emitters.index.values
    # src_makes = [(resources[0]) for _ in range(num_sources)] # Always makes CO2 in our case, so 0
    # sources = list(map(Source, src_idcs, source_locs, src_makes, supply))
    # print("capacity of emissions at source nodes is: ", sum(supply), "Mt")
    #
    # # Facility node input values
    # fac_locs = conversion[["Latitude", "Longitude"]].to_numpy()
    # fac_idcs = conversion.index.values + num_sources # We need to add the number of sources to continue the count
    # num_facs = len(conversion.index)
    #
    # fac_makes = []
    # for i in range (num_facs):
    #     if conversion["End Use"][i] == "urea":
    #         fac_makes.append(resources[1])
    #     elif conversion["End Use"][i] == "methanol":
    #         fac_makes.append(resources[2])
    #     elif conversion["End Use"][i] == "saf":
    #         fac_makes.append(resources[3])
    #
    # fac_needs = [(resources[:1]) for _ in range(num_facs)] # Always needs CO2 in our case
    # facilities = list(map(Facility, fac_idcs, fac_locs, fac_makes, fac_needs))
    #
    # # Sink node input values
    # sink_idcs = consumption.index.values + num_sources + num_facs
    # sink_locs = consumption[["Latitude", "Longitude"]].to_numpy()
    # num_sinks = len(consumption.index)
    #
    # # Demands for different uses
    # urea_demand = []
    # methanol_demand = []
    # saf_demand = []
    #
    # for i in range(num_sinks):
    #     if consumption["Product"][i] == "U":
    #         urea_demand.append(consumption["Demand"][i])
    #     elif consumption["Product"][i] == "M":
    #         methanol_demand.append(consumption["Demand"][i])
    #     elif consumption["Product"][i] == "S":
    #         saf_demand.append(consumption["Demand"][i])
    #
    # urea_demand_total = sum(urea_demand)
    # methanol_demand_total = sum(methanol_demand)
    # saf_demand_total = sum(saf_demand)
    #
    # sink_needs = []
    # for i in range (num_sinks):
    #     if consumption["Product"][i] == "U":
    #         sink_needs.append(resources[1])
    #     elif consumption["Product"][i] == "M":
    #         sink_needs.append(resources[2])
    #     elif consumption["Product"][i] == "S":
    #         sink_needs.append(resources[3])
    #
    # #sink_needs = [resources[-1] for _ in range(num_sinks)] # Always needs SAF in our case
    # sinks = list(map(Sink, sink_idcs, sink_locs, sink_needs, demand))
    # print("capacity of demand at sink nodes is: ", sum(demand), "Mt")
    #
    # # Storage node input values
    # storages_locs = storage[["lat", "long"]].to_numpy()
    # storages_idcs = storage.index.values + num_sources + num_facs + num_sinks
    # num_storages = len(storage.index)
    # storage_needs = [resources[0] for _ in range(num_storages)]
    # storages = list(map(Storage, storages_idcs, storages_locs, storage_needs, stored))
    # print("capacity of storage at storage nodes is: ", sum(stored), "Mt")
    #
    # # Total nodes that will be converted to json
    # nodes = sources + facilities + sinks + storages
    #
    #
    #
    # # Edges. First we construct all source and facility edges. These
    # # represent the construction decisions at the nodes.
    # edges = []
    #
    # for src in sources:
    #     # Capacity for source emissions
    #     capacity = (supply[src.idx]) # If model decides on multiple edges from 1 source this will
    #     # result in greater capacity on the edge than on the source node
    #
    #     # Capture costs, different per industry
    #     cost_per_ton = []
    #     cost_per_ton_Fertilizers = 39.18
    #     cost_per_ton_Cement = 126.81
    #     cost_per_ton_Refineries = 148.79
    #     cost_per_ton_Power_Station = 248.17
    #     cost_per_ton_Iron_and_Steel = 124.30
    #     cost_per_ton_Waste = 39.18
    #
    #     # Append costs to dataframe for each industry
    #     for i in range(num_sources):
    #         if emitters["Industry"][i] == "F":
    #             cost_per_ton.append(cost_per_ton_Fertilizers)
    #
    #         if emitters["Industry"][i] == "C":
    #             cost_per_ton.append(cost_per_ton_Cement)
    #
    #         if emitters["Industry"][i] == "R":
    #             cost_per_ton.append(cost_per_ton_Refineries)
    #
    #         if emitters["Industry"][i] == "PS":
    #             cost_per_ton.append(cost_per_ton_Power_Station)
    #
    #         if emitters["Industry"][i] == "IS":
    #             cost_per_ton.append(cost_per_ton_Iron_and_Steel)
    #
    #         if emitters["Industry"][i]=="D":
    #             cost_per_ton.append(cost_per_ton_Waste)
    #
    #     # Make edge variable from costs to append to edges
    #     cost = cost_per_ton[src.idx]
    #
    #     # Append costs to the edges
    #     edges.append(Edge(src, src, cost, capacity, "B"))
    #
    # for fac in facilities:
    #     # Conversion costs in euro per tonne CO2 for each end-use
    #     conversion_cost_per_ton = []
    #     cost_per_ton_urea = 315.5904
    #     cost_per_ton_methanol = 991.7587
    #     cost_per_ton_saf = 169.1951
    #
    #     for i in range(num_facs):
    #         if conversion["End Use"][i] == "urea":
    #             conversion_cost_per_ton.append(cost_per_ton_urea)
    #         if conversion["End Use"][i] == "methanol":
    #             conversion_cost_per_ton.append(cost_per_ton_methanol)
    #         if conversion["End Use"][i] == "saf":
    #             conversion_cost_per_ton.append(cost_per_ton_saf)
    #
    #     capacity_fac = []
    #     for i in range(num_facs):
    #         if conversion["End Use"][i] == "urea":
    #             capacity_fac.append(urea_demand_total)
    #         if conversion["End Use"][i] == "methanol":
    #             capacity_fac.append(methanol_demand_total)
    #         if conversion["End Use"][i] == "saf":
    #             capacity_fac.append(saf_demand_total)
    #
    #     # Capacity for each facility becomes equal to the demand it produces end products for
    #     capacity = [capacity_fac[fac.idx-num_sources]]
    #
    #     # Make edge variable for conversion costs
    #     cost = conversion_cost_per_ton[fac.idx-num_sources]
    #
    #     # Append vars to edges
    #     edges.append(Edge(fac, fac, cost, capacity, "B"))
    #
    # # All edges BETWEEN source and fac nodes (not self nodes)
    # for inlayer, outlayer in pairwise([sources, facilities]):
    #     sumlist = []
    #     for frm, to in product(inlayer, outlayer):
    #         capacity = frm.supply # Same as supply at source node
    #         sumlist.append(capacity)
    #         cost_src_fac_fixed = 3
    #         cost_src_fac_variable = 0.5 * geopy.distance.geodesic(frm.loc, to.loc).km
    #         cost = cost_src_fac_fixed + cost_src_fac_variable
    #         edges.append(Edge(frm, to, cost, capacity, "C"))
    # print("capacity of CO2 flows along edges going from sources to facilities is: ", sum(sumlist), "(tonnes of total emissions "
    #                                                                                                "at nodes times number of facilities)")
    #
    # # All edges BETWEEN fac and sink nodes (not self nodes)
    # for inlayer, outlayer in pairwise([facilities, sinks]):
    #     sumlist = []
    #     for frm, to in product(inlayer, outlayer):
    #         capacity = to.demand # Same as supply at fac node, which is total demand at the sink node
    #         sumlist.append(capacity)
    #         cost_fac_sink_fixed = 4
    #         cost_fac_sink_variable = 0.5 * geopy.distance.geodesic(frm.loc, to.loc).km
    #         cost = cost_fac_sink_fixed + cost_fac_sink_variable
    #         edges.append(Edge(frm, to, cost, capacity, "C"))
    # print("capacity of end-use demand along edges going from facilities to sinks is: ", sum(sumlist), "(tonnes of total end-use demand "
    #                                                                                                   "times number of facilities)")
    #
    # #All edges BETWEEN source and storage nodes (not self nodes)
    # for inlayer, outlayer in pairwise([sources, storages]):
    #     sumlist = []
    #     for frm, to in product(inlayer, outlayer):
    #         capacity = to.storage # Demand at the storage node
    #         sumlist.append(capacity)
    #         cost_src_storage_fixed = 5
    #         cost_src_storage_variable = 0.6 * geopy.distance.geodesic(frm.loc, to.loc).km
    #         cost = cost_src_storage_fixed + cost_src_storage_variable
    #         edges.append(Edge(frm, to, cost, capacity, "C"))
    # print("capacity of CO2 flow along edges going from sources to storage edges is: ", sum(sumlist), "(tonnes of total storage "
    #                                                                                                  "capacity times number of sources)")
    #
    # # Put all data into file
    # data = ProblemData(
    #     resources=resources, nodes=nodes, edges=edges, num_scenarios=int(1)
    # )
    # return data

def main():
    make_experiment()

if __name__ == "__main__":
    main()
