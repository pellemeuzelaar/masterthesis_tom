import pandas as pd
import folium

# Function to calculate circle size based on emissions


#  CO2 emissions data
df = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Storage/SE/StorageSE.csv")

# make vars
lat = df["Latitude"]
long = df["Longitude"]
sadogf = df["SA or DOGF"]
srl = df["SRL"]

# Get coords and emissions
coords = []
type = []
srllevel = []
for x, y, i, j in zip(lat, long, sadogf, srl):
    coords.append([x, y])
    type.append(i)
    srllevel.append(j)


# Create a map centered on a specific location
m = folium.Map(location=[44.34132222, 28.6497388], tiles="cartodbpositron")
# m = folium.Map(location=[52, 6.6497388], tiles="cartodbpositron")

# star marker
icon_star = folium.Icon(
    prefix='fa',
    icon='star',
    icon_color='yellow',
)


# Add circles to the map based on the emissions data
for coord, typ in zip(coords, type):
    if typ == "DOGF":
        folium.CircleMarker(location=coord, radius=7, color='black', fill=True, fill_opacity=1,
                            fill_color='black').add_to(m)
    if typ == "SA":
        folium.CircleMarker(location=coord, radius=7, color='#737373', fill=True, fill_opacity=0,
                            fill_color='#737373').add_to(m)


for coord, srl in zip(coords, srllevel):
    if srl >= 3:
        folium.Marker(location=coord, icon=icon_star, radius=3, color='black', fill=False, fill_opacity=0,
                      fill_color='black').add_to(m)
    if srl >= 3:
        folium.Marker(location=coord, icon=icon_star, radius=3, color='black', fill=False, fill_opacity=0,
                      fill_color='black').add_to(m)




# Display the map
m.save("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Results/storages.html")
