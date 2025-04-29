import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.basemap import Basemap
from bokeh.plotting import figure, show
import folium


def basemap():
    # data
    df = pd.read_csv("/Users/pellemeuzelaar/PycharmProjects/Thesis_V3/model/data/Emitters/AllEmittersSE.csv", encoding='unicode_escape')
    lats = df["Latitude"]
    lons = df["Longitude"]
    co2_emissions = df["TotalQuantity"]/1000

    print(co2_emissions)

    # Create a Basemap object with the desired projection

    m = Basemap(llcrnrlat=35, urcrnrlat=42, llcrnrlon=18.5, urcrnrlon=27.5,
                resolution='i',projection='tmerc',lon_0=-4.36,lat_0=54.7)


    # Draw coastlines and countries
    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.5)

    # Convert latitude and longitude coordinates to x and y coordinates
    x, y = m(lons, lats)

    # Plot the emissions as circles on the map
    for i in range(len(co2_emissions)):
        circle = plt.Circle((x[i], y[i]), co2_emissions[i], color='blue', alpha=0.5)
        plt.gca().add_artist(circle)

    # Show the plot
    plt.show()


if __name__ == "__main__":
    basemap()
