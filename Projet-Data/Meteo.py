import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import re
import pytz
from pytz import timezone
from bson.objectid import ObjectId

#Connextion à MONGO et récuperation de tous les eléments ==>

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["Projet"]
collection = db["Meteo_Histori"]

results = collection.find()

#CRUD

#1/READ

st.title("Projet YNOV")

st.subheader('Read :')


if(st.button("Affichage des données historique :")):
    data = list(collection.find({},{'_id':0}))
    df = pd.DataFrame(data)
    if df.empty:
        st.error("No data found.")
    else:
        st.dataframe(df)
else:
    st.write("Cliquez sur le bouton pour afficher les données: ")

list_villes = []
for result in results:
    if result['request'].get('query') not in list_villes:
        list_villes.append(result['request'].get('query'))

ville = st.selectbox('Sélectionnez une ville pour voir sa température :' , list_villes)

date_temperature = st.date_input("A quelle date voulez vous chercher la température de la ville")

if date_temperature and ville:
    
    user_date_string = date_temperature.strftime('%Y-%m-%d')    

    result_temperature = list(collection.aggregate([
    
    {"$addFields": {
        "localtimedateonly": {"$substr": ["$location.localtime", 0, 10]}
    }},

    {'$match': {'localtimedateonly': user_date_string, 'request.query': ville}},

    ]))

    if(result_temperature):
            
        lat = pd.DataFrame(result_temperature)['location'][0].get('lat')
        lon = pd.DataFrame(result_temperature)['location'][0].get('lon')
        st.write("La température à : " +ville+ " à la date du : ", date_temperature , "est : " , pd.DataFrame(result_temperature)['current'][0].get('temperature'),' ℃')
        #Add map

        st.map(pd.DataFrame(data={'lat': [float(lat)], 'lon': [float(lon)]}))
    
    else:
        st.write("nous n'avons pas de température enregistrée à cette date pour cette ville")
        
    

if (st.button('Cliquez pour avoir la météo en temps réel :')):

    import requests

    params = {
    'access_key': '45a5958277ad9d67a40385cde79e791a',
    'query': ville
    }

    api_result = requests.get('http://api.weatherstack.com/current', params)

    api_response = api_result.json()

    st.write('La température actuelle à %s est de %d℃' % (api_response['location']['name'], api_response['current']['temperature']))
    st.image(api_response['current']['weather_icons'])

    collection.insert_one(api_response)


#Creaate

st.subheader('Create :')
request_query = st.text_input("Enter location (ex: Paris, France)")
if request_query:
    pattern = "^[a-zA-Z ]+, [a-zA-Z ]+$"
    if re.match(pattern, request_query):
        st.write("Vous avez entré:", request_query)
    else:
        st.warning("Le format n'est pas valide. Voici le format valide : 'Ville, Pays'")
else:
    st.warning("Entrez une ville dans ce format 'City, Country'")

location_parts = request_query.split(",")

location_lat = st.text_input("Location Latitude")
location_lon = st.text_input("Location Longitude")
if (request_query == ''):
    print('      ')
else:
    tz = pytz.timezone("Europe/"+location_parts[0].strip())
    local_time = datetime.now(tz)   

current_temperature = st.text_input("Température actuelle")
image_links = ["https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png", "https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0017_cloudy_with_light_rain.png", "https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png"]
current_weather_icons = st.selectbox("Choisissez une image", image_links)
if current_weather_icons:
    st.image(current_weather_icons, width=300)
vitesse_de_vent_actuelle = st.text_input("Vitesse de vent actuelle")
degré_de_vent_actuel = st.text_input("Degré de vent actuel")
pression_actuelle = st.text_input("Pression actuelle")
précip_actuel = st.text_input("Précipitation actuel")
humidité_actuelle = st.text_input("Humidité actuelle")
couverture_nuageuse_actuelle = st.text_input("Couverture nuageuse actuelle")
sensation_actuelle = st.text_input("Sensation actuelle")
index_uv_actuel = st.text_input("Index uv actuel")
visibilité_actuelle = st.text_input("Visibilité actuelle")

if st.button("Enregistrer"):
    # Create a dictionary of the data
    data = {
        "request": {
            "type": "city",
            "query": request_query,
            "language": "en",
            "unit": "m"
        },
        "location": {
            "name": location_parts[0].strip(),
            "country": location_parts[1].strip(),
            "region": location_parts[1].strip(),
            "lat": location_lat,
            "lon": location_lon,
            "timezone_id": "Europe/Paris",
            "localtime": local_time,
            "localtime_epoch": 1673017560,
            "utc_offset": 1.0
        },
        "current": {
            "observation_time": "02:06 PM",
            "temperature": int(current_temperature),
            "weather_code": 122,
            "weather_icons": [current_weather_icons],
            "weather_descriptions": "Overcast",
            "wind_speed": int(vitesse_de_vent_actuelle),
            "wind_degree": int(degré_de_vent_actuel),
            "wind_dir": "SSW",
            "pressure": int(pression_actuelle),
            "precip": float(précip_actuel),
            "humidity": int(humidité_actuelle),
            "cloudcover": int(couverture_nuageuse_actuelle),
            "feelslike": int(sensation_actuelle),
            "uv_index": int(index_uv_actuel),
            "visibility": int(visibilité_actuelle),
            "is_day": "yes"
        }
    }
    # Insert the data into the MongoDB collection
    collection.insert_one(data)
    st.success("Data saved successfully!")


#Delete

st.subheader('Delete :')

results2 = collection.find()
documents = []
for result in results2:
    location = result["location"]["name"]
    date = result["location"]["localtime"]
    id = result["_id"]
    documents.append(f"{id} - {location} - {date}")

selected_document = st.selectbox("Selectionner un document pour supprimer:", documents)

if st.button("Envoyer"):
    id = selected_document.split(" ")[0]
    selected_doc = collection.find_one({"_id": ObjectId(id)})
    result = collection.delete_one(selected_doc)
    st.success("Document Supprimeé")