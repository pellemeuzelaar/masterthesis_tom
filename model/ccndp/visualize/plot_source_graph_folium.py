import pandas as pd
import folium

# Function to calculate circle size based on emissions
def calculate_circle_radius(emissions):
    # Define the scaling factor as per your requirement
    scaling_factor = 130000
    return emissions / scaling_factor

#  CO2 emissions data
df = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/AllEmittersSE.csv")

# make vars
lat = df["Latitude"]
long = df["Longitude"]
quantity = df["TotalQuantity"]
industry = df["Industry"]

# Get coords and emissions
coords = []
emissions_data = []
for x, y, i in zip(lat, long, quantity):
    coords.append([x, y])
    emissions_data.append(i)

# Create a map centered on a specific location
m = folium.Map(location=[44.34132222, 28.6497388], tiles="cartodbpositron")
# m = folium.Map(location=[52, 6.6497388], tiles="cartodbpositron")


# Add circles to the map based on the emissions data
for coord, emissions, ind in zip(coords, emissions_data, industry):
    if ind == "F":
        radius = calculate_circle_radius(emissions)
        folium.CircleMarker(location=coord, radius=radius, color='green', fill=False, fill_opacity=0, fill_color='green').add_to(m)
    if ind == "C":
        radius = calculate_circle_radius(emissions)
        folium.CircleMarker(location=coord, radius=radius, color='blue', fill=False, fill_opacity=0, fill_color='blue').add_to(m)
    if ind == "R":
        radius = calculate_circle_radius(emissions)
        folium.CircleMarker(location=coord, radius=radius, color='black', fill=False, fill_opacity=0, fill_color='black').add_to(m)
    if ind == "PS":
        radius = calculate_circle_radius(emissions)
        folium.CircleMarker(location=coord, radius=radius, color='red', fill=False, fill_opacity=0, fill_color='red').add_to(m)
    if ind == "IS":
        radius = calculate_circle_radius(emissions)
        folium.CircleMarker(location=coord, radius=radius, color='gray', fill=False, fill_opacity=0, fill_color='gray').add_to(m)
    if ind == "D":
        radius = calculate_circle_radius(emissions)
        folium.CircleMarker(location=coord, radius=radius, color='yellow', fill=False, fill_opacity=0, fill_color='yellow').add_to(m)

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
    <li><span style='background:green;opacity:0.7;'></span>Fertilizer</li>
    <li><span style='background:blue;opacity:0.7;'></span>Cement</li>
    <li><span style='background:black;opacity:0.7;'></span>Refinery</li>
    <li><span style='background:red;opacity:0.7;'></span>Power generation</li>
    <li><span style='background:gray;opacity:0.7;'></span>Iron and steel</li>

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


# Display the map
m.save("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Results/sources.html")
