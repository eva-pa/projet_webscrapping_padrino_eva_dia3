# Fonctions générales
import unicodedata
from geopy.geocoders import Nominatim
from haversine import haversine, Unit
import pandas as pd
# Initialisation de variables
geolocator = Nominatim(user_agent="loc-numbeo")


def RetirerAccentMot(mot):
    return ''.join(c for c in unicodedata.normalize('NFD', mot) if unicodedata.category(c) != 'Mn')


def retirerAccentsListe(listeMots):
    return [RetirerAccentMot(x) for x in listeMots]


def getLatLon(city, country):
    """
    Cette fonction retourne un couple (latitude, longitude)
    pour une ville et un pays donné.

    Parameters
    ----------
    city : str nom de ville
    country : str nom de pays

    Returns
    -------
    latitude : float
    longitude : float

    """
    print(city)
    print(country)
    city = city.partition('(')[0]
    city = 'Cartagena' if city == "Carthagène des Indes" else city
    city = 'Washington Colombie' if city == 'Washington, District de Colombie' else city
    city = city.replace('Nouvelle Ville de Taipei', 'Nouveau Taipei')
    try:
        localisation = geolocator.geocode(f"{city}, {country}'")
    except:
        # if localisation is None else localisation
        localisation = geolocator.geocode(f"{city}, {country}'", timeout=10)

    lat = localisation.latitude
    lon = localisation.longitude

    return lat, lon


def DistanceFromPoint(df, col_lat, col_lon, lat_point, lon_point):
    pointInput = (lat_point, lon_point)
    distances = []
    for index, row in df.iterrows():
        point_df = (row[col_lat], row[col_lon])
        distance = haversine(pointInput, point_df, unit=Unit.METERS)
        distances.append(distance)
    return distances


def SortDistancesAscending(df, col_dist):
    print(df.sort_values(col_dist).head())
    return df.sort_values(col_dist)


def DistanceMax(dist_max, sorted_df, col_dist):
    return sorted_df[sorted_df[col_dist] <= dist_max]


def FiltreSortDf(df, col_dist, dist_max):
    df_cop = df.copy(deep=False)
    df_cop = SortDistancesAscending(df_cop, col_dist)
    df_cop = DistanceMax(dist_max, df_cop, col_dist)
    return df_cop

def ColDict_toCols(df, col_dict):
    """
    Fonction qui permet de mettre en colonnes dans un dataframe 
    les valeurs d'un dictionnaire contenu dans une de ses colonnes.
    Chaque nouvelle colonne porte le nom d'une clé du dictionnaire
    et chaque ligne correspond aux valeurs'

    Parameters
    ----------
    df : dataframe
    col_dict : colonne contenant un dataframe

    Returns
    -------
    datafame avec les nouvelles colonnes

    """
    return  pd.concat([df,df[col_dict].apply(pd.Series)], axis = 1)
"""
def remove_accents(string_list):
    # Créer une liste vide pour stocker les chaînes de caractères sans accent
    no_accents_list = []

    # Pour chaque chaîne de caractères dans la liste de chaînes de caractères
    for string in string_list:
        # Utilisez la fonction unicodedata.normalize pour normaliser la chaîne de caractères en utilisant la forme NFC
        # Cela fusionne tous les caractères composés (comme 'é') en un seul caractère unicode
        normalized_string = unicodedata.normalize('NFC', string)
        # Ensuite, utilisez la fonction .encode() pour encoder la chaîne de caractères en utilisant l'encodage ASCII
        # Cela remplacera tous les caractères qui ne sont pas présents dans l'encodage ASCII par des caractères desubstitution
        # tels que '?' ou ' '.
        ascii_string = normalized_string.encode('ascii', 'replace')
        # Enfin, décodez la chaîne de caractères encodée en ASCII en utilisant l'encodage utf-8 pour obtenir une chaîne de caractères
        # Python standard sans accent
        no_accents_string = ascii_string.decode('utf-8')
        # Ajoutez la chaîne de caractères sans accent à la liste de chaînes de caractères sans accent
        no_accents_list.append(no_accents_string)

    # Retourne la liste de chaînes de caractères sans accent
    return no_accents_list


# Exemple d'utilisation
string_list = ['café', 'français', 'maison']
no_accents_list = remove_accents(string_list)
print(no_accents_list)

import unicodedata 
def strip_accents(s): 
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
"""
