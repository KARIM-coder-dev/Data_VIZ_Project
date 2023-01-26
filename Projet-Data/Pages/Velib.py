import requests
import pandas as pd
import numpy as np
from pymongo import MongoClient
import streamlit as st
import time
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim



def check_alpha_space_string(string):
    for char in string:
        if not (char.isalpha() or char.isspace()):
            return False
    return True

# GET Data
def getvelibData():
    
    url = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&rows=500"
    response = requests.get(url)
    return response.json()  

def stock_into_data(data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Projet']
    collection = db['Velib_Station']
    geolocator = Nominatim(user_agent="geoapiExercice")
    for i in data['records']:
        location = geolocator.reverse(i['fields']['coordonnees_geo'])   
        station_data = {
            'Code_Station':i['fields']['stationcode'],
            'Nom_Station': i['fields']['name'],
            'Geo': i['fields']['coordonnees_geo'],
            'Adress_Station': location.address,
            'E-Velo':i['fields']['ebike'],
            'M-Velo':i['fields']['mechanical'],
            'Velo_disponible': i['fields']['numbikesavailable'],
            'Nombre_de_borne_diponible': i['fields']['numdocksavailable'],
            'Capacité': i['fields']['capacity'],
            'nom_arrondissement_communes': i['fields']['nom_arrondissement_communes']

        }    
        
        collection.insert_one(station_data)



def get_database():
    Client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.1')
    return (Client)

Client = get_database()
db = Client['Projet']
mydata = list(db.Velib_Station.find({}, {'_id':0 , 'Geo': 0}))



# CRUD
st.header('Bienvenue au portail de Velib')
st.caption('Içi vous pouvez chercher votre station la plus proche')

with st.form("Form_Search"):
    adr = st.text_input('Chercher la sation la plus proche de vous'  , placeholder='Exemple: 2, Rue de paris, 75001')
    document = db.Velib_Station.find({'Adress_Station': {"$regex": "^" +adr}}, {'_id':0 , 'nom_arrondissement_communes': 0 , 'Geo': 0})
    submitted = st.form_submit_button("Submit")
    if submitted:
        if (adr != ''):
            st.subheader('Voila les station les plus proches')
            df = pd.DataFrame(document)
            if (df.empty):
                st.warning('Pas de station proche de vous')
            else:    
                st.dataframe(df)  
        else: 
            st.warning("S'il vous plait entre votre adress")


components.iframe(src="https://www.infoclimat.fr/public-api/mixed/iframeSLIDE?_ll=48.85341,2.3488&_inc=WyJQYXJpcyIsIjQyIiwiMjk4ODUwNyIsIkZSIl0=&_auth=AxlTRAN9BiQDLgA3AHZQeQVtBzIIfgUiBXkCYVs%2BUC0HbARlAmJRN1Y4A34HKFJkAC0GZQE6V2dTOAR8WylVNANpUz8DaAZhA2wAZQAvUHsFKwdmCCgFIgVvAmZbKFAxB2cEfgJgUTdWJwNoBzBSeQAsBmcBOFdoUzQEZ1sxVTIDaFMwA2kGewNzAGQAM1A3BWMHYAgyBToFMAJsWzdQYAdjBDICaFEtVj4DaAcwUm8AMQZgAT5XaFMvBHxbT1VFA31TdwMiBjEDKgB%2FAGVQOgVi&_c=a3a641bb1505a0b5702cf8207d994400", width=705, height=350, scrolling=True)

modal = st.expander("Options avancées ")

option_1 = modal.checkbox("Update Data" )
option_2 = modal.checkbox("Delete Data" )
option_3 = modal.checkbox('Charger Data')
option_4 = modal.button('Mise à jour')

if option_1:
    with st.form("Form_Search1"):
        code =  st.text_input('Code Station',placeholder='Exp: 44017')
        nb = st.text_input('Velo Disponible',placeholder='3')
        capicite = st.text_input('Capicite')
        submitted = st.form_submit_button("Submit")
    if submitted:
        if (all(i.isdigit() for i in code) and (4 <= len(code) <= 6)):
            st.success("Match Correcte")
            res = db.Velib_Station.find({'Code_Station': code})
            if  res:
                db.Velib_Station.update_one({'Code_Station': code}, {'$set':{'Velo_disponible': nb , 'Capacité': capicite}})
            else: 
                st.error("Ce code de station n'existe pas")
        else: 
            st.error("Verifier vos données")  

if option_2:
    with st.form("Form_Search2"):
        code = st.text_input('Code Station',placeholder='10000') 
        print(code)
        submitted1 = st.form_submit_button("Submit")
    if submitted1:
        if (all(i.isdigit() for i in code) and (4 <= len(code) <= 6)):
            document = list(db.Velib_Station.find({'Code_Station': code}))
            if document:
                db.Velib_Station.delete_one({'Code_Station': code})
                st.success("Document deleted successfully.")
            else: 
                st.error('Ce code ne correspond a aucun station')
        else:
            st.error("Verifier vos données, Code Station entre 4 et 6 chiffres")      

if option_3:
    with st.spinner('Chargement...'):
        time.sleep(3)
        df = []
        df = pd.DataFrame(mydata)
        if df.empty:
            st.error('Pas de donnees')
        else:    
            st.dataframe(df)

if option_4:
    data = getvelibData()
    stock_into_data(data)
    st.success('Ces donnes sont mis a jour')




