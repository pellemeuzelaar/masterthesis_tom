import pandas as pd
import folium

# Function to calculate circle size based on emissions
def calculate_circle_radius(emissions):
    # Define the scaling factor as per your requirement
    scaling_factor = 1000
    return emissions / scaling_factor

#  CO2 emissions data
df = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Facilities/SE/ORBIS_SE.csv")

# make vars
name = df["Company"]
lat = df["Latitude"]
long = df["Longitude"]
product = df["Product"]

for i in range(len(df["Product"])):
    if product[i] == "Urea":
        df["Capacity"] = 178.59
    elif product[i] == "Methanol":
        df["Capacity"] = 72.66
    elif product[i] == "SAF":
        df["Capacity"] = 324.94

capacity = df["Capacity"]


# Get coords and emissions
coords = []
capacity_data = []
for x, y, i in zip(lat, long, capacity):
    coords.append([x, y])
    capacity_data.append(i)

# Create a map centered on a specific location
m = folium.Map(location=[44.34132222, 28.6497388], tiles="cartodbpositron") #SE
#m = folium.Map(location=[52, 6.6497388], tiles="cartodbpositron") #NW


# Add circles to the map based on the emissions data
for coord, idx, ind in zip(coords, name, product):
    if ind == "Urea":
        radius = 3
        folium.CircleMarker(location=coord, radius=radius, color='green', fill=False, fill_opacity=1, fill_color='green', popup = folium.Popup(idx)).add_to(m)
    if ind == "Methanol":
        radius = 3
        folium.CircleMarker(location=coord, radius=radius, color='blue', fill=False, fill_opacity=1, fill_color='blue', popup = folium.Popup(idx)).add_to(m)
    if ind == "SAF":
        radius = 3
        folium.CircleMarker(location=coord, radius=radius, color='red', fill=False, fill_opacity=1, fill_color='red', popup = folium.Popup(idx)).add_to(m)

# Add legend
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
m.save("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Results/facsSE.html")
