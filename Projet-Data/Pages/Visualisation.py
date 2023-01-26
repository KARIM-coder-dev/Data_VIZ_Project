import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt

import plotly.graph_objects as go
import pymongo



st.set_page_config(page_title="Data Visualization", page_icon=":chart_with_upwards_trend:", layout="wide")

def variation_temperature():
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["Projet"]
    collection = db["Meteo_Histori"]
    # Get all documents from the collection
    docs = collection.find({})
    df = pd.DataFrame(columns=['City', 'Temperature Variation'])
    for doc in docs:
        city = doc["location"]["name"]
        temperature = doc["current"]["temperature"]
        if city in df["City"].values:
            df.loc[df["City"] == city, "Temperature Variation"] = temperature
        else:
            df = df.append({"City": city, "Temperature Variation": temperature}, ignore_index=True)
   
    df1 = df
    df2 = df1.set_index("City")
    st.title("Répartition des températures par ville")
    st.line_chart(df2)

def borne_dispo():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["Projet"]
    collection = db["Velib_Station"]
    # Retrieve data from the collection
    data = list(collection.find({}))
    # Convert the data to a dataframe
    df = pd.DataFrame(data)
    df = df.groupby("Nom_Station").sum()
    df = df.sort_values("Velo_disponible", ascending=True)
    
    st.title("Nombre de vélos disponibles par borne")
    # Plot the data using streamlit
    st.bar_chart(df["Velo_disponible"])
def Evelo_MVelo_par_station():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["Projet"]
    collection = db["Velib_Station"]
    data = list(collection.find().sort("Nombre_de_borne_diponible", pymongo.DESCENDING).limit(10))
    df = pd.DataFrame(data)
    st.title("  Top 10 des stations qui contiennent le plus de vélos disponibles + Comparaison entre Vélos électriques et mécaniques")
    st.bar_chart(df.groupby("Nom_Station").sum()[["E-Velo","M-Velo"]])    


def velib_map():
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/Météo")
    db = client["Projet"]
    collection = db["Velib_Station"]
    # Retrieve data from the collection
    data = list(collection.find({}, {'_id':0}))

    lat = [coord['Geo'][0] for coord in data]
    lon = [coord['Geo'][1] for coord in data]
    df = pd.DataFrame({"lat": lat, "lon": lon})

    fig = go.Figure(go.Scattermapbox(lat=df["lat"], lon=df["lon"], mode='markers'))
    st.title("Répartition des stations de vélib par adresses : graphique en carte")
    fig.update_layout(mapbox_style="open-street-map", 
    autosize=True,margin=dict(l=0, r=0, t=0, b=0),mapbox=dict(center=go.layout.mapbox.Center(lat=48.8566, lon=2.3522), zoom=12))
    st.write(fig)


    


variation_temperature() 
borne_dispo()
Evelo_MVelo_par_station()
velib_map()
      

            



    
    

    
    





