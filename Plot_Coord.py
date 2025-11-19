#https://www.edriessen.com/notebooks/maps-with-geopandas-matplotlib.html
#https://geopandas.org/en/stable/docs/user_guide/mapping.html
#https://www.geeksforgeeks.org/python/convert-files-from-jpg-to-gif-and-vice-versa-using-python/
#https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python
#https://stackoverflow.com/questions/11373610/save-matplotlib-file-to-a-directory
#https://stackoverflow.com/questions/44505196/how-to-display-an-image-using-tkinter-in-gui
#https://documenter.getpostman.com/view/664302/S1ENwy59 ebird access documentation
#https://siansiansu.github.io/ebird-country/
#https://www.geeksforgeeks.org/python/multithreading-python-set-1/
#https://stackoverflow.com/questions/20190668/multiprocessing-a-for-loop
#lots of stackoverflow

#tutorial used
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
import pandas as pd
import json
from dotenv import load_dotenv
import requests
import matplotlib.pyplot as plt
from shapely.geometry import Point
import imageio
import os
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError

load_dotenv()

def plot_coord():
    #creating res folder for easy access
    script_dir = os.path.dirname(__file__)
    maps_dir = os.path.join(script_dir, 'Maps/')
    if not os.path.isdir(maps_dir):
        os.makedirs(maps_dir)

    #bird section
    API_KEY = os.getenv("API_KEY")
    bird_list_data = []

    #read through local json file
    with open("Birds.json", "r") as f:
        bird_list_data = json.load(f)

    bird_coords = []
    #loop through all selected birds
    #add multithreading here -------------------------
    def multithread_Birds(args):
        bird = args
        speciesCode = bird["code"]

        eBird_url = f"https://api.ebird.org/v2/data/obs/US/recent/{speciesCode}"

        params = {"back": 2, "maxResults": 100}#limiting maxResults because there are a lot of birds
        headers = {"X-eBirdApiToken": API_KEY}
            
        birdres = requests.get(eBird_url, headers = headers, params = params)
        try:
            bird_data = birdres.json()
        except JSONDecodeError:
            print("Invalid JSON from eBird:", birdres.text)
            return []
        print(bird_data)
        #convert to list comprehension
        return [
            {
                "lat": data.get("lat"),
                "lng": data.get("lng"),
                "obsDt": datetime.strptime(data["obsDt"], "%Y-%m-%d %H:%M").isoformat()
            }
            for data in bird_data
            if " " in data.get("obsDt", "")
        ]

    tasks = [bird for bird in bird_list_data]

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(multithread_Birds, tasks))
    bird_coords = [item for sublist in results for item in sublist]

    with open("bird_coords.json", "w") as f:
        json.dump(bird_coords, f)
        
    current_time = datetime.now()

    for bird in bird_coords:
        bird_dt = datetime.fromisoformat(bird["obsDt"])
        bird["hour"] = bird_dt.hour
        bird["date"] = bird_dt.date()


    #i just asked chatgpt to find me an online GeoJSON map
    america = gpd.read_file("https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json")
    america = america.query("name not in ['Alaska', 'Hawaii', 'Puerto Rico']")
    
    #change this back to 23 for full testing
    for hours_ago in range(23,-1,-1):
        target_time = current_time - timedelta(hours=hours_ago)
        target_hours_date = (target_time.hour, target_time.date())
        filtered_birds_by_hour = [
            {"lat": bird["lat"], "lng": bird["lng"]}
            for bird in bird_coords
            if (bird["hour"], bird["date"]) == target_hours_date
        ]
        print("filter bird",filtered_birds_by_hour)
        balloon_time = hours_ago
        if balloon_time < 10:
            balloon_time = '0'+str(balloon_time)
        else:
            balloon_time = str(balloon_time)
            
        #pull weatherballoon data from .json
        print("weather balloon file,",balloon_time)
        balloonData = 'https://a.windbornesystems.com/treasure/'+balloon_time+'.json'
        print("balloon data",balloonData)
        req = requests.get(balloonData)
        try:
            coords = req.json()
        except JSONDecodeError:
            print("Invalid JSON from Windborne Systems:", balloon_time)
            return []

        #create dataframe with coords
        #0 = latitude and 1 = longitude from balloon .json file
        #crs for real world reference datapoints
        
        min_lat, max_lat = 24.52, 49.38    # US latitude
        min_lon, max_lon = -124.77, -66.95 # US longitude
        
        df = pd.DataFrame(coords)
        df['geo'] = [Point(xy) for xy in zip(df[1], df[0])]
        geo_df = gpd.GeoDataFrame(df, geometry = 'geo', crs='EPSG:4326')
        filtered_geo_df = geo_df[(geo_df[0] >= min_lat) & (geo_df[0] <= max_lat) &(geo_df[1] >= min_lon) & (geo_df[1] <= max_lon)]
        if filtered_birds_by_hour:
            bird_df = pd.DataFrame(filtered_birds_by_hour)
            bird_df['geo'] = [Point(xy) for xy in zip(bird_df['lng'], bird_df['lat'])]
            bird_gdf = gpd.GeoDataFrame(bird_df, geometry = 'geo', crs='EPSG:4326')
            filtered_bird_gdf = bird_gdf[(bird_gdf['lat'] >= min_lat) & (bird_gdf['lat'] <= max_lat) &(bird_gdf['lng'] >= min_lon) & (bird_gdf['lng'] <= max_lon)]
                    
        fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

        america.plot(ax=ax, color='lightblue', edgecolor='black', linewidth=0.5)

        filtered_geo_df.plot(ax=ax, color='red', markersize=15)

        if filtered_birds_by_hour:
            filtered_bird_gdf.plot(ax=ax, color='purple', markersize=20)

        ax.set_title("Weather Balloons and Common Birds in the US at " + str(target_time.date()) + " " + str(target_time.hour)+":00 UTC", fontsize=16)

        plt.savefig(maps_dir + str(balloon_time) + ".jpg", dpi=300, bbox_inches='tight')
        plt.close(fig)


