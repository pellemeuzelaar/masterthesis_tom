# Script to summarize the result data

import pandas as pd
import json


def main():
    # Opening files
    f = open("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Results/BASE_MULTI_NW.json")
    emitters = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/AllEmittersNW(kg:y).csv")
    emitters["TotalQuantity (kg/year)"] = emitters["TotalQuantity (kg/year)"]/1000000000
    conversion = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Facilities/NW/Facilities_NW_ALL.csv")
    consumption = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Demand/NW/Demand_NW_ALL_USES.csv")
    storage = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Storage/Storage_NW_2.csv")
    storage["yearly_capacity"] = 3.51875 # this is the mean returned by the line below

    # Facs to sink locs
    num_src = len(emitters)
    num_fac = len(emitters) + len(conversion)
    num_sink = len(emitters) + len(conversion) + len(consumption)
    num_storage = len(emitters) + len(conversion) + len(consumption) + len(storage)

    # returns JSON object as a dictionary
    data = json.load(f)

    ### CAPTURE COSTS ###

    # Empty lists for strg
    counter_list = []
    amount_captured = []

    # Find the amount CO2 stored in storages and transport costs
    for i in range(num_src):
        counter = "source[" + str(i) + "]"
        if data["decisions"][counter] >= 1:
            counter_list.append(counter)
            amount_captured.append(emitters["TotalQuantity (kg/year)"][i])

    capture_costs = []
    for i in counter_list:
        capture_costs.append(data["decision_costs"][i])

    # And print this into df
    df_list = []
    for i, j, s in zip(counter_list, amount_captured, capture_costs):
        df_list.append([i, j, s])
    df_src = pd.DataFrame(df_list, columns=["Source edge", "Emissions captured", "Capture costs"])
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

    urea_demand_total = sum(urea_demand)
    methanol_demand_total = sum(methanol_demand)
    saf_demand_total = sum(saf_demand)


    # Empty list for facilities
    fac_capacity = 2
    counter_list = []

    # Capacity and costs of selected facilities
    for i in range(num_src, num_fac):
        counter = "facility[" + str(i) + "]"
        if data["decisions"][counter] > 0:
            counter_list.append(counter)

    conversion_costs = []
    for i in counter_list:
        conversion_costs.append(data["decision_costs"][i])

    # Print facility capacities
    df_list = []
    print("\nFacilities selected and the amount of end-product they produce (equal shares assumed)")
    for i, j, s in zip(counter_list, fac_capacity, conversion_costs):
        df_list.append([i,j,s])
    df_fac = pd.DataFrame(df_list, columns=["Facility", "Quantity produced", "Conversion costs"])
    df_fac.set_index("Facility", inplace=True)
    print(df_fac)

    ### SINK DEMAND ###

    # Empty lists for locs sink
    df_sink = pd.DataFrame(consumption, columns=["Demand"])
    df_sink.index.name="Sink"
    print(df_sink)

    ### EDGES ###

    ### SOURCE - > FAC EDGES ###

    # Empty lists for locs fac edges
    counter_list = []
    amount_supplied = []

    # Find the amount CO2 stored in storages and transport costs
    for i in range(num_src):
        for j in range(num_src, num_fac):
            counter = "source[" + str(i) + "] -> facility[" + str(j) + "]"
            if data["decisions"][counter] > 0:
                counter_list.append(counter)
                amount_supplied.append(emitters["TotalQuantity (kg/year)"][i])

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
    print(df_src_fac)

    ### FAC - > SINK EDGES ###

    # Empty lists for locs fac edges
    counter_list = []
    amount_demanded = []

    # Find the amount end use transport and transport costs
    for i in range(num_src, num_fac):
        for j in range(num_fac, num_sink):
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
    df_fac_sink = pd.DataFrame(df_list, columns=["Facility to sink edge", "Amount demanded", "Edge decision",
                                                 "Transport costs to sink"])
    df_fac_sink.set_index("Facility to sink edge", inplace=True)
    df_fac_sink["Final quantity end product transport"] = df_fac_sink["Edge decision"] * df_fac_sink["Amount demanded"]
    df_fac_sink["Final costs"] = df_fac_sink["Edge decision"] * df_fac_sink["Transport costs to sink"]
    print(df_fac_sink)

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
                amount_stored.append(storage["yearly_capacity"][j-num_sink])

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
    total_emissions_not_captured = sum(emitters["TotalQuantity"]) - sum(amount_captured)

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
    total_converted_amount = sum(df_fac_sink["Final quantity end product transport"])

    # Total transport costs of products from facs to sinks
    total_end_use_transport_costs = sum(df_fac_sink["Final costs"])

    # Sink
    # Sink demand
    total_sink_demand = sum(consumption["Demand"])

    # Storage
    # Total CO2 stored
    total_co2_stored = sum(df_src_strg["Final quantity stored"])

    # Total transport costs of CO2 to storages
    total_storage_transport_costs = sum(df_src_strg["Final costs"])




    # Total costs of supply chain
    objective_function = total_capture_costs + total_co2_transport_costs + total_conversion_costs + \
                         total_end_use_transport_costs + total_storage_transport_costs

    # Display the values
    print("\nTotal quantity of CO2 captured with by the emitter building decisions: ", total_emissions_captured)
    print("Total quantity of CO2 that is not captured as they are not built: ", total_emissions_not_captured)
    print("\nTotal amount CO2 transferred from sources to facilities: ", total_amount_co2_transport)
    print("Note that when multiple CO2 flows out of 1 source edge, the above number does not represent the right"
          "amount of flow. Namely, each flow is the max emissions for the respective source. So divide by number"
          "of flows from this source if necessary.")
    print("Total amount end product transferred from facs to sinks: ", total_converted_amount)
    print("Note that when multiple CO2 flows out of 1 facility edge, the above number does not represent the right"
          "amount of flow. Namely, each flow is the max production for the respective fac. So divide by number"
          "of flows from this fac if necessary.")
    print("\nTotal amount CO2 transferred to storages: ", total_co2_stored)
    print("Total end product demand: ", total_sink_demand)

    print("\nThe total costs of the supply chain are: ", objective_function)

if __name__ == "__main__":
    main()
