import pandas as pd
import folium
import json
import re
from folium.plugins import BeautifyIcon


def main():

    ### GET DATA AND GET THE DECISIONS ###

    # Opening files
    f = open("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Results/BASE_MULTI_UK_V2.json")
    emitters = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/NW/AllEmittersUK(kg:y).csv")
    conversion = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Facilities/NW/Facilities_UK.csv")
    consumption = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Demand/NW/Demand_NW_UK.csv")
    storage = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Storage/NW/Storage_UK.csv")

    # returns JSON object as a dictionary
    data = json.load(f)

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
        if number < num_src:
            src_decisions.append(number)
        if number >= num_src and number < num_fac:
            fac_decisions.append(number)

    # Specify the end-uses for the fac and sink decisions
    urea_fac_decisions = (set(fac_decisions) & set(idcs_fac_urea))
    methanol_fac_decisions = (set(fac_decisions) & set(idcs_fac_methanol))
    saf_fac_decisions = (set(fac_decisions) & set(idcs_fac_saf))

    # All sinks are included:
    sink_decisions = []
    for i in range(len(consumption)):
        sink_decisions.append(i + num_fac)

    urea_sink_decisions = (set(sink_decisions) & set(idcs_sink_urea))
    methanol_sink_decisions = (set(sink_decisions) & set(idcs_sink_methanol))
    saf_sink_decisions = (set(sink_decisions) & set(idcs_sink_saf))



    # Add storage decisions manually:
    strg_decisions = []

    # Find all edge decisions
    all_edges = []
    for i in decision_name:
        all_edges.append(re.findall('\d+', i))
    edges = []
    for sublist in all_edges:
        if len(sublist) == 2:
            edges.append(sublist)

    # Get frm and to edges
    frm = [item[0] for item in edges]
    to = [item[1] for item in edges]
    frm = [eval(i) for i in frm]
    to = [eval(i) for i in to]

    # Make distinction for frm between src, fac:
    frm_src_to_fac = []
    frm_src_to_strg = []
    frm_fac = []
    for i in frm:
        if i <= num_src:
            frm_src_to_fac.append(i)
        if i > num_src and i <= num_fac:
            frm_fac.append(i)

    # Make distinction for to between fac, sink and strg:
    to_fac = []
    to_sink = []
    to_strg = []
    for i in to:
        if i >= num_src and i < num_fac:
            to_fac.append(i)
        if i >= num_fac and i < num_sink:
            to_sink.append(i)
        if i >= num_sink and i < num_storage:
            to_strg.append(i)

    # Make distinction for frm source to storage and update the frm_sources to exclude frm_sources to strg:
    # frm_src_to_strg = frm_src_to_fac[-len(to_strg):]
    # frm_src_to_fac = frm_src_to_fac[:-len(frm_src_to_strg)]

    # Find the locations of the selected sources:
    src_lat = []
    src_long = []
    for i in src_decisions:
        src_lat.append(emitters["Latitude"][i])
        src_long.append(emitters["Longitude"][i])

    # Find the locations of the selected urea facs:
    fac_lat_urea = []
    fac_long_urea = []
    for i in urea_fac_decisions:
        fac_lat_urea.append(conversion["Latitude"][i - num_src])
        fac_long_urea.append(conversion["Longitude"][i - num_src])

    # Find the locations of the selected methanol facs:
    fac_lat_methanol = []
    fac_long_methanol = []
    for i in methanol_fac_decisions:
        fac_lat_methanol.append(conversion["Latitude"][i - num_src])
        fac_long_methanol.append(conversion["Longitude"][i - num_src])

    # Find the locations of the selected saf facs:
    fac_lat_saf = []
    fac_long_saf = []
    for i in saf_fac_decisions:
        fac_lat_saf.append(conversion["Latitude"][i - num_src])
        fac_long_saf.append(conversion["Longitude"][i - num_src])

    # Find the locations of the selected urea sinks:
    sink_lat_urea = []
    sink_long_urea = []
    for i in urea_sink_decisions:
        sink_lat_urea.append(consumption["Latitude"][i - num_fac])
        sink_long_urea.append(consumption["Longitude"][i - num_fac])

    # Find the locations of the selected methanol sinks:
    sink_lat_methanol = []
    sink_long_methanol = []
    for i in methanol_sink_decisions:
        sink_lat_methanol.append(consumption["Latitude"][i - num_fac])
        sink_long_methanol.append(consumption["Longitude"][i - num_fac])

    # Find the locations of the selected saf sinks:
    sink_lat_saf = []
    sink_long_saf = []
    for i in saf_sink_decisions:
        sink_lat_saf.append(consumption["Latitude"][i - num_fac])
        sink_long_saf.append(consumption["Longitude"][i - num_fac])

    # Find locations of storages:
    strg_lat = []
    strg_long = []
    for i in strg_decisions:
        strg_lat.append(storage["Latitude"][i - num_sink])
        strg_long.append(storage["Longitude"][i - num_sink])

    # Plot a map with the nodes
    m = folium.Map(location=[53.34132222, 4.6497388], tiles="CartoDBpositron")


    ### EDGES ###

    # Create lists for emitters to facilities
    edges_src_lat = []
    edges_src_lon = []
    edges_fac_lat = []
    edges_fac_lon = []

    # Emitters to facilities edges
    for i, j in zip(frm_src_to_fac, to_fac):
        edges_src_lat.append(emitters["Latitude"][i])
        edges_src_lon.append(emitters["Longitude"][i])
        edges_fac_lat.append(conversion["Latitude"][j - num_src])
        edges_fac_lon.append(conversion["Longitude"][j - num_src])

    # Create the actual lines between srcs and facs on the map (edges)
    coordinates_from = []
    coordinates_to = []
    coordinates = []
    for i, j, x, y in zip(edges_src_lat, edges_src_lon, edges_fac_lat, edges_fac_lon):
        coordinates_from.append([i, j])
        coordinates_to.append([x, y])
    for i, j in zip(coordinates_from, coordinates_to):
            coordinates.append([i, j])
    my_PolyLine = folium.PolyLine(locations=coordinates, color='black', weight='3')
    m.add_child(my_PolyLine)

    # Create lists for facs to sinks
    edges_fac_lat = []
    edges_fac_lon = []
    edges_sink_lat = []
    edges_sink_lon = []
    # urea fac to sink edges
    for i in urea_sink_decisions:
        for j in urea_fac_decisions:
            edges_fac_lat.append(conversion["Latitude"][j - num_src])
            edges_fac_lon.append(conversion["Longitude"][j - num_src])
            edges_sink_lat.append(consumption["Latitude"][i - num_fac])
            edges_sink_lon.append(consumption["Longitude"][i - num_fac])

    # Create the actual lines between facs and sinks on the map (edges)
    coordinates_from = []
    coordinates_to = []
    coordinates = []
    for i, j, x, y in zip(edges_fac_lat, edges_fac_lon, edges_sink_lat, edges_sink_lon):
        coordinates_from.append([i, j])
        coordinates_to.append([x, y])
    for i, j in zip(coordinates_from, coordinates_to):
        coordinates.append([i, j])
    my_PolyLine = folium.PolyLine(locations=coordinates, color='#737373', weight='1', dash_array='3')
    m.add_child(my_PolyLine)

    # Create lists for facs to sinks
    edges_fac_lat = []
    edges_fac_lon = []
    edges_sink_lat = []
    edges_sink_lon = []

    # methanol fac to sink edges
    for i in methanol_sink_decisions:
        for j in methanol_fac_decisions:
            edges_fac_lat.append(conversion["Latitude"][j - num_src])
            edges_fac_lon.append(conversion["Longitude"][j - num_src])
            edges_sink_lat.append(consumption["Latitude"][i - num_fac])
            edges_sink_lon.append(consumption["Longitude"][i - num_fac])

    # Create the actual lines between facs and sinks on the map (edges)
    coordinates_from = []
    coordinates_to = []
    coordinates = []
    for i, j, x, y in zip(edges_fac_lat, edges_fac_lon, edges_sink_lat, edges_sink_lon):
        coordinates_from.append([i, j])
        coordinates_to.append([x, y])
    for i, j in zip(coordinates_from, coordinates_to):
        coordinates.append([i, j])
    my_PolyLine = folium.PolyLine(locations=coordinates, color='#737373', weight='1', dash_array='3')
    m.add_child(my_PolyLine)

    # Create lists for facs to sinks
    edges_fac_lat = []
    edges_fac_lon = []
    edges_sink_lat = []
    edges_sink_lon = []

    # saf fac to sink edges
    for i in saf_sink_decisions:
        for j in saf_fac_decisions:
            edges_fac_lat.append(conversion["Latitude"][j - num_src])
            edges_fac_lon.append(conversion["Longitude"][j - num_src])
            edges_sink_lat.append(consumption["Latitude"][i - num_fac])
            edges_sink_lon.append(consumption["Longitude"][i - num_fac])

    # Create the actual lines between facs and sinks on the map (edges)
    coordinates_from = []
    coordinates_to = []
    coordinates = []
    for i, j, x, y in zip(edges_fac_lat, edges_fac_lon, edges_sink_lat, edges_sink_lon):
        coordinates_from.append([i, j])
        coordinates_to.append([x, y])
    for i, j in zip(coordinates_from, coordinates_to):
        coordinates.append([i, j])
    my_PolyLine = folium.PolyLine(locations=coordinates, color='#737373', weight='1', dash_array='3')
    m.add_child(my_PolyLine)

    # Create lists for sources to storages:##################
    edges_src_lat = []
    edges_src_lon = []
    edges_strg_lat = []
    edges_strg_lon = []

    # From src to storage edges
    for i, j in zip(frm_src_to_strg, to_strg):
        edges_src_lat.append(emitters["Latitude"][i])
        edges_src_lon.append(emitters["Longitude"][i])
        edges_strg_lat.append(storage["Latitude"][j - num_sink])
        edges_strg_lon.append(storage["Longitude"][j - num_sink])

    # Create the actual lines between srcs and storages on the map (edges)
    coordinates_from = []
    coordinates_to = []
    coordinates = []
    for i, j, x, y in zip(edges_src_lat, edges_src_lon, edges_strg_lat, edges_strg_lon):
        coordinates_from.append([i, j])
        coordinates_to.append([x, y])
    for i, j in zip(coordinates_from, coordinates_to):
        coordinates.append([i, j])
    # my_PolyLine = folium.PolyLine(locations=coordinates, color='black', weight='3')
    # m.add_child(my_PolyLine)





    ### NODES ###



    # Add emitters nodes
    for i in range(len(src_decisions)):
        folium.CircleMarker(
            location=([src_lat[i], src_long[i]]),
            radius=11,
            fill=False,
            fill_opacity=1,
            fill_color="black",
            color="black",
            popup=folium.Popup(emitters["Latitude"][i])
        ).add_to(m)

    # Add fac nodes urea
    for i in range(len(urea_fac_decisions)):
        folium.RegularPolygonMarker(
            location=([fac_lat_urea[i], fac_long_urea[i]]),
            number_of_sides=3,
            rotation=30,
            radius=10,
            fill=False,
            fill_opacity=1,
            fill_color="green",
            color="green",
            popup=folium.Popup(i)
        ).add_to(m)

    # Add fac nodes methanol
    for i in range(len(methanol_fac_decisions)):
        folium.RegularPolygonMarker(
            location=([fac_lat_methanol[i], fac_long_methanol[i]]),
            number_of_sides=3,
            rotation= 30,
            radius=10,
            fill=False,
            fill_opacity=1,
            fill_color="blue",
            color="blue",
            popup=folium.Popup(i)
        ).add_to(m)

    # Add fac nodes saf
    for i in range(len(saf_fac_decisions)):
        folium.RegularPolygonMarker(
            location=([fac_lat_saf[i], fac_long_saf[i]]),
            number_of_sides=3,
            rotation=30,
            radius=10,
            fill=False,
            fill_opacity=1,
            fill_color="red",
            color="red",
            popup=folium.Popup(i)
        ).add_to(m)

    # Add urea sink nodes
    for i in range(len(urea_sink_decisions)):
        icon_square = BeautifyIcon(
            icon_shape='rectangle-dot',
            border_color='green',
            border_width=6,)
        folium.Marker(
            location=([sink_lat_urea[i], sink_long_urea[i]]),
            tooltip='square',
            icon=icon_square,
            fill=False,
        ).add_to(m)


    # Add methanol sink nodes
    for i in range(len(methanol_sink_decisions)):
        icon_square = BeautifyIcon(
            icon_shape='rectangle-dot',
            border_color='blue',
            border_width=6)
        folium.Marker(
            location=([sink_lat_methanol[i], sink_long_methanol[i]]),
            tooltip='square',
            icon=icon_square,
            fill=False,
            fill_color="blue",
            color="blue",
            popup=folium.Popup(i)
        ).add_to(m)

    # Add saf sink nodes
    for i in range(len(saf_sink_decisions)):
        icon_square=BeautifyIcon(
            icon_shape='rectangle-dot',
            border_color='red',
            border_width=6)
        folium.Marker(
            location=([sink_lat_saf[i], sink_long_saf[i]]),
            tooltip='square',
            icon=icon_square,
            fill=False,
            fill_color="blue",
            color="blue",
            popup=folium.Popup(i)
        ).add_to(m)

    # Add storage nodes
    # for i in range(len(strg_decisions)):
    #     folium.CircleMarker(
    #         location=([strg_lat[i], strg_long[i]]),
    #         radius=11,
    #         fill=False,
    #         color="black",
    #         popup=folium.Popup(i)
    #     ).add_to(m)






    # Create legend
    from branca.element import Template, MacroElement
    template = """
    {% macro html(this, kwargs) %}

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>jQuery UI Draggable - Default functionality</title>
      <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

      <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

      <script>
      $( function() {
        $( "#maplegend" ).draggable({
                        start: function (event, ui) {
                            $(this).css({
                                right: "auto",
                                top: "auto",
                                bottom: "auto"
                            });
                        }
                    });
    });

      </script>
    </head>
    <body>


    <div id='maplegend' class='maplegend' 
        style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
         border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

    <div class='legend-title'>Legend</div>
    <div class='legend-scale'>
      <ul class='legend-labels'>
        <li><span style='background:green;opacity:0.7;'></span>Urea plant</li>
        <li><span style='background:blue;opacity:0.7;'></span>Methanol plant</li>
        <li><span style='background:red;opacity:0.7;'></span>SAF plant</li>
        <li><span style='background:black;opacity:0.7;'></span>CO2 source</li>
        <li><span style='background:grey;opacity:0.7;'></span>End-use (truck) transport (dashed)</li>
        <li><span style='background:black;opacity:0.7;'></span>CO2 (pipeline) transport</li>

      </ul>
    </div>
    </div>

    </body>
    </html>

    <style type='text/css'>
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    {% endmacro %}"""

    macro = MacroElement()
    macro._template = Template(template)

    m.get_root().add_child(macro)



    # Save the map
    m.save("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Results/BASE_MULTI_UK_V2.html")

    # Closing file
    f.close()

if __name__ == "__main__":
    main()
