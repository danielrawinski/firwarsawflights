import requests
import pandas as pd
import fiona
from shapely.geometry import shape, Point, Polygon
import streamlit as st

# =============================================================================
# Request for aircraft data
# =============================================================================

# Coordinates of a square around Poland
lomin = 14.12298
lamin = 49.002024
lomax = 24.14585
lamax = 55.849717

url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"

response=requests.get(url).json()

# Loading to pandas
col_name=['icao24','callsign','origin_country','time_position','last_contact','long','lat','baro_altitude','on_ground','velocity',       
'true_track','vertical_rate','sensors','geo_altitude','squawk','spi','position_source']
flight_df=pd.DataFrame(response['states'],columns=col_name)
flight_df=flight_df.fillna('No Data') #replace NAN with No Data
flight_df.head()

# =============================================================================
# Creating points and checking if in Poland
# =============================================================================

# get the shapes
c = fiona.open('FIRWarszawa_epsg_4326.shp')  #opening in fiona to get a list of coordinates later
pol = next(iter(c)) #list of coordinates within a layer

# build a shapely polygon from your shape
polygon = Polygon(pol["geometry"]["coordinates"][0])

p1 = Point(flight_df.iloc[1]["long"], flight_df.iloc[1]["lat"])
p1.within(polygon)

flight_df["long"].apply(lambda x: float(x))
flight_df["lat"].apply(lambda x: float(x))

flight_df["point"] = flight_df.apply(lambda x: Point(x["long"], x["lat"]), axis=1)
flight_df["in_poland"] = flight_df.apply(lambda x: x["point"].within(polygon), axis=1)

# =============================================================================
# Page body & results counter
# =============================================================================

st.header("The number of aircraft over FIR Warszawa")
st.write("""FIR Warszawa is a region of airspace, encompassing Poland land and water territory and part of Baltic Sea further north
         that is controlled by air traffic controllers from Warsaw. As in every region, the capacity to guide aircraft safely is limited by space and human factors. 
         This application shows how many aircraft is currently over FIR Warszawa territory; a functionality of viewing historical records is planned to be added.""")
         
st.write(f"Number of planes currently over Poland: **{str(flight_df['in_poland'].tolist().count(True))}**")

st.write("Sources:")
st.write("[Flight information from Open Flights](https://openflights.org/data.html)")
st.write("FIR Warszawa map: own production based on Poland shapefile from [GUGIK](http://www.gugik.gov.pl/pzgik/dane-bez-oplat/dane-z-panstwowego-rejestru-granic-i-powierzchni-jednostek-podzialow-terytorialnych-kraju-prg) and [FIR Warszawa definition from Journal of Laws of the Republic of Poland](http://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20190000619)")
