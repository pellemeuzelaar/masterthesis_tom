# Script to summarize the result data

import pandas as pd
import re
import json


def main():
    # Opening files
    f = open("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Results/2_MULTI_RO_SA.json")
    emitters = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/SE/AllEmittersRO(t:y).csv")
    emitters["TotalQuantity(tons/y)"] = emitters["TotalQuantity(tons/y)"]/1000000
    conversion = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Facilities/SE/SE_ALL_FAC_RO.csv")
    consumption = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Demand/SE/Demand_SE_ALL_RO.csv")
    storage = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Storage/SE/StorageRO.csv")
    storage["yearly_capacity"] = 3.52 # this is the mean returned by the line below
    # returns JSON object as a dictionary
    data = json.load(f)

    # Facs to sink locs
    num_src = len(emitters)
    num_fac = len(conversion) + len(emitters)
    num_sink = len(emitters) + len(conversion) + len(consumption)
    num_storage = len(emitters) + len(conversion) + len(consumption) + len(storage)

    # differentiate between facs and sink types
    idcs_fac_urea = []
    for i in range(len(conversion)):
        if conversion["Product"][i] == "Urea":
            idcs_fac_urea.append(i + num_src)
    idcs_fac_methanol = []
    for i in range(len(conversion)):
        if conversion["Product"][i] == "Methanol":
            idcs_fac_methanol.append(i + num_src)
    idcs_fac_saf = []
    for i in range(len(conversion)):
        if conversion["Product"][i] == "SAF":
            idcs_fac_saf.append(i + num_src)
    idcs_sink_urea = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "Urea":
            idcs_sink_urea.append(i + num_fac)
    idcs_sink_methanol = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "Methanol":
            idcs_sink_methanol.append(i + num_fac)
    idcs_sink_saf = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "SAF":
            idcs_sink_saf.append(i + num_fac)

    # Find decisions bigger than 0:
    values = []
    for i in data["decisions"]:
        values.append(data["decisions"][i])


    ### CAPTURE COSTS ###

    # Empty lists for strg
    counter_list = []
    amount_captured = []
    industry = []

    # Find the amount CO2 stored in storages and transport costs
    for i in range(num_src):
        counter = "source[" + str(i) + "]"
        if data["decisions"][counter] >= 1:
            counter_list.append(counter)
            amount_captured.append(emitters["TotalQuantity(tons/y)"][i])
            industry.append(emitters["Industry"][i])

    capture_costs = []
    for i in counter_list:
        capture_costs.append(data["decision_costs"][i])

    # And print this into df
    df_list = []
    for i, j, s, p in zip(counter_list, amount_captured, capture_costs, industry):
        df_list.append([i, j, s, p])
    df_src = pd.DataFrame(df_list, columns=["Source edge", "Emissions captured", "Capture costs", "Industry"])
    df_src.set_index("Source edge", inplace=True)
    print(df_src)


    ### FACILITIES CONVERSION COST ###

    # Capacity
    urea_demand = []
    methanol_demand = []
    saf_demand = []

    for i in range(len(consumption)):
        if consumption["Product"][i] == "Urea":
            urea_demand.append(consumption["Demand (Kton/year)"][i])
        elif consumption["Product"][i] == "Methanol":
            methanol_demand.append(consumption["Demand (Kton/year)"][i])
        elif consumption["Product"][i] == "SAF":
            saf_demand.append(consumption["Demand (Kton/year)"][i])

    # Empty list for facilities
    fac_capacity = [2 for i in range(num_fac)]
    counter_list = []
    name = []

    for i in range(num_src, num_fac):
        counter = "facility[" + str(i) + "]"
        if data["decisions"][counter] >= 1:
            counter_list.append(counter)
            name.append(conversion["Company"][i - num_src])

    conversion_costs = []
    for i in counter_list:
        conversion_costs.append(data["decision_costs"][i])

    # Print facility capacities
    df_list = []
    print("\nFacilities selected and the amount of end-product they produce (equal shares assumed)")
    for n, i, j, s in zip(name, counter_list, fac_capacity, conversion_costs):
        df_list.append([n, i, j, s])
    df_fac = pd.DataFrame(df_list, columns=["Name", "Facility", "Quantity produced", "Conversion costs"])
    df_fac.set_index("Facility", inplace=True)
    print(df_fac)

    ### SINK DEMAND ###

    # Empty lists for locs sink
    df_sink = pd.DataFrame(consumption, columns=["Demand (Kton/year)"])
    df_sink.index.name="Sink"
    print(df_sink)

    ### EDGES ###

    ### SOURCE - > FAC EDGES ###

    # Empty lists for locs fac edges
    counter_list = []
    amount_supplied = []
    supplied = emitters["TotalQuantity(tons/y)"]/2

    # Find the amount CO2 stored in storages and transport costs
    for i in range(num_src):
        for j in range(num_src, num_fac):
            counter = "source[" + str(i) + "] -> facility[" + str(j) + "]"
            if data["decisions"][counter] > 0:
                counter_list.append(counter)
                amount_supplied.append(supplied[i])

    transport_costs_co2 = []
    transport_co2_edge_decisions = []
    for i in counter_list:
        transport_costs_co2.append(data["decision_costs"][i])
        transport_co2_edge_decisions.append(data["decisions"][i])

    # And print this into df
    df_list = []
    for i, j, s, k in zip(counter_list, amount_supplied, transport_co2_edge_decisions, transport_costs_co2):
        df_list.append([i, j, s, k])
    df_src_fac = pd.DataFrame(df_list, columns=["Source to facility edge", "Amount supplied", "Edge decision",
                                                "Transport costs to fac"])
    df_src_fac.set_index("Source to facility edge", inplace=True)
    df_src_fac["Final costs"] = df_src_fac["Edge decision"] * df_src_fac["Transport costs to fac"]
    df_src_fac["Final quantity CO2 transport"] = df_src_fac["Edge decision"] * df_src_fac["Amount supplied"]
    df_src_fac["Final costs"] = df_src_fac["Edge decision"] * df_src_fac["Transport costs to fac"]
    print(df_src_fac["Final quantity CO2 transport"])

    ### FAC - > SINK EDGES ###

    # differentiate between facs and sink types
    idcs_fac_urea = []
    for i in range(len(conversion)):
        if conversion["Product"][i] == "Urea":
            idcs_fac_urea.append(i + num_src)
    idcs_fac_methanol = []
    for i in range(len(conversion)):
        if conversion["Product"][i] == "Methanol":
            idcs_fac_methanol.append(i + num_src)
    idcs_fac_saf = []
    for i in range(len(conversion)):
        if conversion["Product"][i] == "SAF":
            idcs_fac_saf.append(i + num_src)
    idcs_sink_urea = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "Urea":
            idcs_sink_urea.append(i + num_fac)
    idcs_sink_methanol = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "Methanol":
            idcs_sink_methanol.append(i + num_fac)
    idcs_sink_saf = []
    for i in range(len(consumption)):
        if consumption["Product"][i] == "SAF":
            idcs_sink_saf.append(i + num_fac)

    # Find decisions bigger than 0:
    values = []
    for i in data["decisions"]:
        values.append(data["decisions"][i])

    # Put them in a list:
    decisions_string = data["decisions"]
    decision_value = []
    decision_name = []
    for i, j in zip(values, decisions_string):
        if i > 0:
            decision_value.append(i)
            decision_name.append(j)

    # Extract the values of the nodes within the decisions and make a list of decisions:
    src_decisions = []
    fac_decisions = []

    for i in decision_name:
        number = int(''.join(filter(str.isdigit, i)))
        if number <= num_src:
            src_decisions.append(number)
        if number >= num_src and number < num_fac:
            fac_decisions.append(number)

    # Specify the end-uses for the fac and sink decisions
    urea_fac_decisions = (set(fac_decisions) & set(idcs_fac_urea))
    methanol_fac_decisions = (set(fac_decisions) & set(idcs_fac_methanol))
    saf_fac_decisions = (set(fac_decisions) & set(idcs_fac_saf))




    # Empty lists for locs fac edges
    counter_list = []
    amount_demanded = []

    # Find the amount UREA end use transport and transport costs
    for i in urea_fac_decisions:
        for j in idcs_sink_urea:
            counter = "facility[" + str(i) + "] -> sink[" + str(j) + "]"
            if data["decisions"][counter] > 0:
                counter_list.append(counter)
                amount_demanded.append(consumption["Demand (Kton/year)"][j-num_fac])

    transport_costs_end_use = []
    transport_end_use_edge_decisions = []
    for i in counter_list:
        transport_costs_end_use.append(data["decision_costs"][i])
        transport_end_use_edge_decisions.append(data["decisions"][i])

    # And print this into df
    df_list = []
    for i, j, s, k in zip(counter_list, amount_demanded, transport_end_use_edge_decisions, transport_costs_end_use):
        df_list.append([i, j, s, k])
    df_fac_sink_urea = pd.DataFrame(df_list, columns=["Facility to UREA sink edge", "Amount demanded", "Edge decision",
                                                 "Transport costs to sink"])
    df_fac_sink_urea.set_index("Facility to UREA sink edge", inplace=True)
    df_fac_sink_urea["Final quantity end product transport"] = df_fac_sink_urea["Edge decision"] * df_fac_sink_urea["Amount demanded"]
    df_fac_sink_urea["Final costs"] = df_fac_sink_urea["Edge decision"] * df_fac_sink_urea["Transport costs to sink"]
    print(df_fac_sink_urea)



    # Empty lists for locs fac edges
    counter_list = []
    amount_demanded = []

    # Find the amount METHANOL end use transport and transport costs
    for i in methanol_fac_decisions:
        for j in idcs_sink_methanol:
            counter = "facility[" + str(i) + "] -> sink[" + str(j) + "]"
            if data["decisions"][counter] > 0:
                counter_list.append(counter)
                amount_demanded.append(consumption["Demand (Kton/year)"][j-num_fac])

    transport_costs_end_use = []
    transport_end_use_edge_decisions = []
    for i in counter_list:
        transport_costs_end_use.append(data["decision_costs"][i])
        transport_end_use_edge_decisions.append(data["decisions"][i])

    # And print this into df
    df_list = []
    for i, j, s, k in zip(counter_list, amount_demanded, transport_end_use_edge_decisions, transport_costs_end_use):
        df_list.append([i, j, s, k])
    df_fac_sink_methanol = pd.DataFrame(df_list, columns=["Facility to METHANOL sink edge", "Amount demanded", "Edge decision",
                                                 "Transport costs to sink"])
    df_fac_sink_methanol.set_index("Facility to METHANOL sink edge", inplace=True)
    df_fac_sink_methanol["Final quantity end product transport"] = df_fac_sink_methanol["Edge decision"] * df_fac_sink_methanol["Amount demanded"]
    df_fac_sink_methanol["Final costs"] = df_fac_sink_methanol["Edge decision"] * df_fac_sink_methanol["Transport costs to sink"]
    print(df_fac_sink_methanol)



    # Empty lists for locs fac edges
    counter_list = []
    amount_demanded = []

    # Find the amount SAF end use transport and transport costs
    for i in saf_fac_decisions:
        for j in idcs_sink_saf:
            counter = "facility[" + str(i) + "] -> sink[" + str(j) + "]"
            if data["decisions"][counter] > 0:
                counter_list.append(counter)
                amount_demanded.append(consumption["Demand (Kton/year)"][j-num_fac])

    transport_costs_end_use = []
    transport_end_use_edge_decisions = []
    for i in counter_list:
        transport_costs_end_use.append(data["decision_costs"][i])
        transport_end_use_edge_decisions.append(data["decisions"][i])

    # And print this into df
    df_list = []
    for i, j, s, k in zip(counter_list, amount_demanded, transport_end_use_edge_decisions, transport_costs_end_use):
        df_list.append([i, j, s, k])
    df_fac_sink_saf = pd.DataFrame(df_list, columns=["Facility to SAF sink edge", "Amount demanded", "Edge decision",
                                                 "Transport costs to sink"])
    df_fac_sink_saf.set_index("Facility to SAF sink edge", inplace=True)
    df_fac_sink_saf["Final quantity end product transport"] = df_fac_sink_saf["Edge decision"] * df_fac_sink_saf["Amount demanded"]
    df_fac_sink_saf["Final costs"] = df_fac_sink_saf["Edge decision"] * df_fac_sink_saf["Transport costs to sink"]
    print(df_fac_sink_saf)



    ### SOURCE - > STORAGE EDGES ###

    # Empty lists for strg
    counter_list = []
    amount_stored = []


    # Find the amount CO2 stored in storages and transport costs
    for i in range(num_src):
        for j in range(num_sink, num_storage):
            counter = "source[" + str(i) + "] -> node[" + str(j) + "]"
            if data["decisions"][counter] > 0:
                counter_list.append(counter)
                amount_stored.append(emitters["TotalQuantity(tons/y)"][i])

    storage_edge_decisions = []
    storage_costs = []
    for i in counter_list:
        storage_costs.append(data["decision_costs"][i])
        storage_edge_decisions.append(data["decisions"][i])

    # And print this into df
    df_list = []
    for i, j, s, k in zip(counter_list, amount_stored, storage_edge_decisions, storage_costs):
        df_list.append([i, j, s, k])
    df_src_strg = pd.DataFrame(df_list, columns=["Source to storage edge", "Capacity stored",
                                                 "Storage transport decisions", "Storage transport costs"])
    df_src_strg.set_index("Source to storage edge", inplace=True)
    df_src_strg["Final quantity stored"] = df_src_strg["Storage transport decisions"] * df_src_strg["Capacity stored"]
    df_src_strg["Final costs"] = df_src_strg["Storage transport decisions"] * df_src_strg["Storage transport costs"]
    print(df_src_strg)

    ### DATA INSIGHTS ###

    # Sources
    # Emissions captured
    total_emissions_captured = sum(amount_captured)
    total_emissions_not_captured = sum(emitters["TotalQuantity(tons/y)"]) - sum(amount_captured)

    # Total capture costs
    total_capture_costs = sum(capture_costs)

    # Total amount of CO2 transported to facs
    total_amount_co2_transport = sum(df_src_fac["Final quantity CO2 transport"])

    # Total CO2 transport costs to facs
    total_co2_transport_costs = sum(df_src_fac["Final costs"])

    # Facilities
    # Conversion amount
    total_conversion_costs = sum(conversion_costs)

    # Total amount of end product converted
    total_converted_amount_urea = sum(df_fac_sink_urea["Final quantity end product transport"])
    total_converted_amount_methanol = sum(df_fac_sink_methanol["Final quantity end product transport"])
    total_converted_amount_saf = sum(df_fac_sink_saf["Final quantity end product transport"])

    # Total transport costs of products from facs to sinks
    total_urea_transport_costs = sum(df_fac_sink_urea["Final costs"])
    total_methanol_transport_costs = sum(df_fac_sink_methanol["Final costs"])
    total_saf_transport_costs = sum(df_fac_sink_saf["Final costs"])
    total_end_use_transport_costs = total_urea_transport_costs + total_methanol_transport_costs + total_saf_transport_costs

    # Sink
    # Sink demand
    total_sink_demand = sum(consumption["Demand (Kton/year)"])

    # Storage
    # Total CO2 stored
    total_co2_stored = sum(df_src_strg["Final quantity stored"])

    # Total transport costs of CO2 to storages
    total_storage_transport_costs = sum(df_src_strg["Final costs"])




    # Total costs of supply chain
    objective_function = total_capture_costs + total_co2_transport_costs + total_conversion_costs + \
                         total_end_use_transport_costs + total_storage_transport_costs


    # Display the values
    print("total emissions by all nodes are: ", sum(emitters["TotalQuantity(tons/y)"]))
    print("Total quantity of CO2 captured with by the emitter building decisions: ", total_emissions_captured)
    print("Total quantity of CO2 that is not captured as they are not built: ", total_emissions_not_captured)
    print("Total CO2 capacities of storage building decisions: ", total_co2_stored)


    print("\ntotal source nodes: ", len(src_decisions))
    print("total facility nodes: ", len(fac_decisions))
    print("total sink nodes: ", num_sink)
    print("total storage nodes: ", )



    print("\nTotal urea demand: ", sum(urea_demand))
    print("Total methanol demand: ", sum(methanol_demand))
    print("Total SAF demand: ", sum(saf_demand))
    print("Total end product demand: ", total_sink_demand)



    print("\ncapture costs: ", total_capture_costs)
    print("transport CO2 costs to facs: ", total_co2_transport_costs)
    print("conversion costs at facs: ", total_conversion_costs)
    print("transport costs end-uses (truck): ", total_end_use_transport_costs)
    print("pipeline costs to storage: ", total_storage_transport_costs)
    print("\nThe total costs of the supply chain are: ", objective_function)

if __name__ == "__main__":
    main()
