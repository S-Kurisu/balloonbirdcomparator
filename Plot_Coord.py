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

    #found a list of eBird region codes and had chatgpt make me a list of strings
    eBird_countries = [
        "AF", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AC",
        "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT",
        "BO", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI", "KH", "CM", "CA",
        "CV", "BQ", "KY", "CF", "TD", "CL", "CN", "CX", "CP", "CC", "CO", "KM", "CG",
        "CK", "CS", "CR", "CI", "HR", "CU", "CW", "CY", "CZ", "DK", "DJ", "DM", "DO",
        "CD", "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET", "FK", "FO", "FJ", "FI",
        "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD",
        "GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT", "HM", "XX", "HN", "HK", "HU",
        "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO",
        "KZ", "KE", "KI", "XK", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI",
        "LT", "LU", "MO", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU",
        "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR",
        "NP", "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "KP", "MK", "NO",
        "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR",
        "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN", "LC", "MF", "PM", "VC", "WS",
        "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SK", "SI", "SB", "SO",
        "ZA", "GS", "KR", "SS", "ES", "LK", "SD", "SR", "SJ", "SE", "CH", "SY", "TW",
        "TJ", "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV",
        "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VA", "VE", "VN", "VG",
        "VI", "WF", "EH", "YE", "ZM", "ZW"
    ]
    #read through local json file
    with open("Birds.json", "r") as f:
        bird_list_data = json.load(f)

    bird_coords = []
    #loop through all selected birds
    #add multithreading here -------------------------
    def multithread_Birds(args):
        bird, countryCode = args
        speciesCode = bird["code"]

        eBird_url = f"https://api.ebird.org/v2/data/obs/{countryCode}/recent/{speciesCode}"

        params = {"back": 2, "maxResults": 100}#limiting maxResults because there are a lot of birds
        headers = {"X-eBirdApiToken": API_KEY}
            
        birdres = requests.get(eBird_url, headers = headers, params = params)
        bird_data = birdres.json()
        if not bird_data:
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

    tasks = [(bird, countryCode) for bird in bird_list_data for countryCode in eBird_countries]

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
    world = gpd.read_file("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json")
        
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
        coords = req.json()

        #create dataframe with coords
        #0 = latitude and 1 = longitude from balloon .json file
        #crs for real world reference datapoints
        df = pd.DataFrame(coords)
        df['geo'] = [Point(xy) for xy in zip(df[1], df[0])]
        geo_df = gpd.GeoDataFrame(df, geometry = 'geo', crs='EPSG:4326')
        
        if filtered_birds_by_hour:
            bird_df = pd.DataFrame(filtered_birds_by_hour)
            bird_df['geo'] = [Point(xy) for xy in zip(bird_df['lng'], bird_df['lat'])]
            bird_gdf = gpd.GeoDataFrame(bird_df, geometry = 'geo', crs='EPSG:4326')
                    
        fig, ax = plt.subplots(figsize=(8, 6), dpi=200)

        world.plot(ax=ax, color='lightblue', edgecolor='black', linewidth=0.5)

        geo_df.plot(ax=ax, color='red', markersize=5)

        if filtered_birds_by_hour:
            bird_gdf.plot(ax=ax, color='purple', markersize=10)

        ax.set_title("Weather Balloons at " + str(target_time.hour)+":00", fontsize=16)

        plt.savefig(maps_dir + str(balloon_time) + ".jpg", dpi=200, bbox_inches='tight')
        plt.close(fig)
#----------------abandoned gif functionality-----------------------
#create gif
#images = []
#for map in maps:
#    images.append(imageio.v2.imread(map))
#imageio.mimsave(script_dir+'/1 day map.gif', images, duration=len(maps)*500, loop=0)


