"""
Makes the random instances used in the numerical experiments section of the
paper. See there for details. By Pelle Meuzelaar, 2023

Current IDX data summary:
Emitters: 0-211
Facilities: 212-309
Sinks: 310-363
Storages: 364-517 (mostly SRL 0 assumed)
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
    print("NODE DATA:")
    resources = [Resource(0, "CO2"), Resource(1, "Urea"), Resource(2, "E-methanol"), Resource(3, "SAF")]

    # Supply node data and correct the scale of quantity, which is now in kg and needs to be tonne
    emitters = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/NW/AllEmittersNW(kg:y).csv")
    emitters = pd.DataFrame(emitters)

    # Facility node data
    conversion = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Facilities/NW/Facilities_NW_saf.csv")
    conversion = pd.DataFrame(conversion)

    # Demand node data
    consumption = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Demand/NW/Demand_NW_SAF.csv")
    consumption = pd.DataFrame(consumption)

    # Storage node data
    storage = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Storage/NW/Storage_NW.csv")
    storage = pd.DataFrame(storage)

    # The values inputted for different nodes imported from dataframe
    supply = emitters.iloc[:,4:].values/1000000000 # Is in Kt Convert to Mton
    demand = consumption.iloc[:,5:].values/1000 # Is in Kt, convert to Mton
    stored = storage.iloc[:,7:].values # Is in Mt, convert to ton
    num_sinks = len(consumption.index)
    num_facs = len(conversion.index)

    # Source node input values, facilities, and sinks, and what they make and need.
    source_locs = emitters[["Latitude", "Longitude"]].to_numpy()
    num_sources = len(emitters.index)
    src_idcs = emitters.index.values
    src_makes = [(resources[0]) for _ in range(num_sources)] # Always makes CO2 in our case, so 0
    sources = list(map(Source, src_idcs, source_locs, src_makes, supply))

    # Facility node input values
    urea_fac_makes = [] # 1 for urea
    urea_fac_needs = [] # Always needs CO2 in our case
    urea_fac_locs = []
    urea_fac_idcs = []
    for i in range (len(conversion)):
        if conversion["Product"][i] == "Urea":
            urea_fac_makes.append(resources[1])
            urea_fac_needs.append((resources[:1]))
            urea_fac_idcs.append(i + num_sources)
            lat = conversion["Latitude"][i]
            long = conversion["Longitude"][i]
            urea_fac_locs.append([lat, long])

    # Make a urea specific node
    urea_facilities = list(map(Facility, urea_fac_idcs, urea_fac_locs, urea_fac_makes, urea_fac_needs))

    # Fac with just methanol
    methanol_fac_makes = []
    methanol_fac_needs = []  # Always needs CO2 in our case
    methanol_fac_locs = []
    methanol_fac_idcs = []
    for i in range(len(conversion)):
        if conversion["Product"][i] == "Methanol":
            methanol_fac_makes.append((resources[2]))
            methanol_fac_needs.append((resources[:1]))
            methanol_fac_idcs.append(i + num_sources)
            lat = conversion["Latitude"][i]
            long = conversion["Longitude"][i]
            methanol_fac_locs.append([lat, long])

    # Make a methanol specific node
    methanol_facilities = list(map(Facility, methanol_fac_idcs, methanol_fac_locs, methanol_fac_makes, methanol_fac_needs))

    # Fac with just SAF
    saf_fac_makes = [] # 1 for urea
    saf_fac_needs = []
    saf_fac_locs = []
    saf_fac_idcs = []
    for i in range(len(conversion)):
        if conversion["Product"][i] == "SAF":
            saf_fac_makes.append((resources[3]))
            saf_fac_needs.append((resources[:1]))
            saf_fac_idcs.append(i + num_sources)
            lat = conversion["Latitude"][i]
            long = conversion["Longitude"][i]
            saf_fac_locs.append([lat, long])

    # SAF specific node
    saf_facilities = list(map(Facility, saf_fac_idcs, saf_fac_locs, saf_fac_makes, saf_fac_needs))

    # Map with just urea sinks
    urea_sink_needs = []
    urea_sink_locs = []
    urea_sink_idcs = []
    urea_demand = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "Urea":
            urea_sink_needs.append((resources[1]))
            urea_sink_idcs.append(i + num_sources + num_facs)
            lat = consumption["Latitude"][i]
            long = consumption["Longitude"][i]
            urea_sink_locs.append([lat, long])
            urea_demand.append(demand[i])

    # Urea specific sink
    urea_sinks = list(map(Sink, urea_sink_idcs, urea_sink_locs, urea_sink_needs, urea_demand))

    # Map with just methanol sinks
    methanol_sink_needs = []
    methanol_sink_locs = []
    methanol_sink_idcs = []
    methanol_demand = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "Methanol":
            methanol_sink_needs.append((resources[2]))
            methanol_sink_idcs.append(i + num_sources + num_facs)
            lat = consumption["Latitude"][i]
            long = consumption["Longitude"][i]
            methanol_sink_locs.append([lat, long])
            methanol_demand.append(demand[i])

    # Methanol specific sink
    methanol_sinks = list(map(Sink, methanol_sink_idcs, methanol_sink_locs, methanol_sink_needs, methanol_demand))

    # Map with just saf sinks
    saf_sink_needs = []
    saf_sink_locs = []
    saf_sink_idcs = []
    saf_demand = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "SAF":
            saf_sink_needs.append((resources[3]))
            saf_sink_idcs.append(i + num_sources + num_facs)
            lat = consumption["Latitude"][i]
            long = consumption["Longitude"][i]
            saf_sink_locs.append([lat, long])
            saf_demand.append(demand[i])

    # SAF specific sink
    saf_sinks = list(map(Sink, saf_sink_idcs, saf_sink_locs, saf_sink_needs, saf_demand))

    # Storage node input values
    storages_locs = storage[["Latitude", "Longitude"]].to_numpy()
    storages_idcs = storage.index.values + num_sources + num_facs + num_sinks
    num_storages = len(storage.index)
    storage_needs = [(resources[0]) for _ in range(num_storages)]
    storages = list(map(Storage, storages_idcs, storages_locs, storage_needs, stored))

    # All node together become

    nodes = sources + urea_facilities + methanol_facilities + saf_facilities + urea_sinks + methanol_sinks + saf_sinks + storages

    print("Total emissions at ALL (possible) source nodes is: ", sum(supply), "Mt")
    print("Total yearly capacity at storage nodes is: ", sum(stored), "Mt")
    print("Total demand for all end-users yearly is: ", sum(urea_demand + methanol_demand + saf_demand), "Mt")
    print("Total demand for urea yearly is: ", sum(urea_demand), "Mt")
    print("Total demand for methanol yearly is: ", sum(methanol_demand), "Mt")
    print("Total demand for saf yearly is: ", sum(saf_demand), "Mt")






    ### EDGES ###
    print("EDGE DATA:")

    # First we construct all source and facility edges. These
    # represent the construction decisions at the nodes.
    edges = []

    for src in sources:
        # Capacity for source emissions
        capacity = supply[src.idx] # If model decides on multiple edges from 1 source this will
        # result in greater capacity on the edge than on the source node

        # Capture costs, different per industry, per ton to per mton
        cost_per_ton = [] # is in fact cost per Mton
        cost_per_ton_Fertilizers = 25950000 #25.95  per ton
        cost_per_ton_Cement = 95790000 #95.79  per ton
        cost_per_ton_Refineries = 16610000 #16.61 per ton
        cost_per_ton_Power_Station = 79020000 #79.02 per ton
        cost_per_ton_Iron_and_Steel = 99970000 #99.97 per ton
        cost_per_ton_Waste = 25950000 #25.95 per ton

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
        capacity_nobrackets = capacity.tolist()
        capacity_nobrackets = str(capacity_nobrackets)
        capacity_nobrackets = capacity_nobrackets.replace('[', '').replace(']', '')
        capacity_nobrackets = float(capacity_nobrackets)
        cost = capacity_nobrackets*cost_per_ton[src.idx]

        # Append costs to the edges
        edges.append(Edge(src, src, cost, capacity, "B"))

    for fac in urea_facilities:
        # Conversion costs in euro per tonne CO2 for each end-use
        cost_per_ton_urea = 458470000
        capacity_urea_plants = 1.5 #Mton
        cost = cost_per_ton_urea
        capacity = [capacity_urea_plants]

        edges.append(Edge(fac, fac, cost, capacity, "B"))

    for fac in methanol_facilities:
        # Conversion costs in euro per tonne CO2 for each end-use
        cost_per_ton_methanol = 700630000
        capacity_methanol_plants = 1.5 #Mton
        cost = cost_per_ton_methanol
        capacity = [capacity_methanol_plants]

        edges.append(Edge(fac, fac, cost, capacity, "B"))

    for fac in saf_facilities:
        # Conversion costs in euro per tonne CO2 for each end-use
        cost_per_ton_saf = 190000000
        capacity_saf_plants = 1.5 #Mton
        cost = cost_per_ton_saf
        capacity = [capacity_saf_plants]

        edges.append(Edge(fac, fac, cost, capacity, "B"))

    # All edges BETWEEN source and fac nodes
    for inlayer, outlayer in pairwise([sources, urea_facilities]):
        for frm, to in product(inlayer, outlayer):
            capacity = [1.10] # maximum co2 needed based on the CO2 feedstock required (0.73 Mton for 1 Mton urea)
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost_capital = 24.7*((1.10*31.71)**0.35)*((1000*distance)**1.13)
            capex_annual = cost_capital/50
            cost_OM_pipeline = 0.02 * cost_capital # Opex as percentage
            cost = capex_annual + cost_OM_pipeline # + cost_site_capex_opex
            edges.append(Edge(frm, to, cost, capacity, "C"))

    # All edges BETWEEN source and fac nodes
    for inlayer, outlayer in pairwise([sources, methanol_facilities]):
        for frm, to in product(inlayer, outlayer):
            capacity = [2.06]
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost_capital = 24.7*((2.06*31.71)**0.35)*((1000*distance)**1.13)
            capex_annual = cost_capital/50
            cost_OM_pipeline = 0.02 * cost_capital # Opex as percentage
            cost = capex_annual + cost_OM_pipeline # + cost_site_capex_opex
            edges.append(Edge(frm, to, cost, capacity, "C"))

    # All edges BETWEEN source and fac nodes
    for inlayer, outlayer in pairwise([sources, saf_facilities]):
        for frm, to in product(inlayer, outlayer):
            capacity = [4.50] # [3.16] Same as supply at source node, not more than the pipeline capacity of 3.5MT
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost_capital = 24.7*((4.50*31.71)**0.35)*((1000*distance)**1.13)
            capex_annual = cost_capital/50
            cost_OM_pipeline = 0.02 * cost_capital # Opex as percentage
            cost = capex_annual + cost_OM_pipeline # + cost_site_capex_opex
            edges.append(Edge(frm, to, cost, capacity, "C"))

    # All edges BETWEEN urea fac and urea sink nodes
    for inlayer, outlayer in pairwise([urea_facilities, urea_sinks]):
        sumlist = []
        for frm, to in product(inlayer, outlayer):
            capacity = to.demand # Same as supply at fac node, which is total demand at the sink node
            sumlist.append(capacity)
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost = (100000*distance) #  cost is 0.1eur/t per ton
            edges.append(Edge(frm, to, cost, capacity, "C"))

    print("urea --> wholesaler capacity ", sum(sumlist), "Mt")

    # All edges BETWEEN methanol fac and methanol sink nodes
    for inlayer, outlayer in pairwise([methanol_facilities, methanol_sinks]):
        sumlist = []
        for frm, to in product(inlayer, outlayer):
            capacity = to.demand  # Same as supply at fac node, which is total demand at the sink node
            sumlist.append(capacity)
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost = (100000*distance) #  cost is 0.1eur/t per ton
            edges.append(Edge(frm, to, cost, capacity, "C"))

    print("methanol --> port capacity ", sum(sumlist), "Mt")

    # All edges BETWEEN saf fac and saf sink nodes
    for inlayer, outlayer in pairwise([saf_facilities, saf_sinks]):
        sumlist = []
        for frm, to in product(inlayer, outlayer):
            capacity = to.demand  # Same as supply at fac node, which is total demand at the sink node
            sumlist.append(capacity)
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost = (100000*distance) #  cost is 0.1eur/t per ton
            edges.append(Edge(frm, to, cost, capacity, "C"))

    print("saf --> airport capacity ", sum(sumlist), "Mt")





    #All edges BETWEEN source and storage nodes
    for inlayer, outlayer in pairwise([sources, storages]):
        for frm, to in product(inlayer, outlayer):
            capacity = [3.52] # Same as supply at source node, not more than the pipeline capacity of 3.5MT
            distance = geopy.distance.geodesic(frm.loc, to.loc).km
            cost_capital = 24.7*((3.52*31.71)**0.35)*((1000*distance)**1.13)
            capex_annual = cost_capital/50
            cost_OM_pipeline = 0.02 * cost_capital # Opex as percentage
            cost = capex_annual + cost_OM_pipeline # + cost_site_capex_opex
            edges.append(Edge(frm, to, cost, capacity, "C"))


    # Put all data into file
    data = ProblemData(
        resources=resources, nodes=nodes, edges=edges, num_scenarios=1
    )
    return data

def main():
    data = make_experiment()
    data.to_file("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Instances/STORAGE_MULTI_NW_saf_SA.json")

if __name__ == "__main__":
    main()
