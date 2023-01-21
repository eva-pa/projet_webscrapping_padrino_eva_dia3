from fonctionsGen import getLatLon, DistanceFromPoint, FiltreSortDf, ColDict_toCols
from glassdoorscrap import SalaireNumbeoPoints, GetRatio
import os
import pandas as pd
import plotly.graph_objs as go


# Visualiser : Index seuls, ratios ou salaires seuls.


def VisuIndex(ville, pays, distance_max):
    """
    Premier niveau:
        On veut obtenir juste les index de coûts de la vie dans les villes
        les plus proches de notre point (en dessous d'une distance max) dans la table
                                    numbeo.
                                        

    Parameters
    ----------
    ville : str, ville de notre choix
    pays : str, pays de la ville.
    distance_max : float| int, distance max entre notre point et ceux de la table numbeo

    Returns
    -------
    df : dataframe ordonné par distance (de la + proche jusqu'à la + lointaine')
     contenant les index de coûts de la vie.

    """
    # On cherche la latitude et longitude correspondant àla localisation entrée
    lat_point, lon_point = getLatLon(ville, pays)
    #Chargement table numbeo
    path = os.getcwd()    
    file_name = '{}\\numbeo\\tabAll\\tabAllCountries_v3.csv'.format(path)
    df = pd.read_csv(file_name)
    # On garde dans la table numbeo les points proches en dessous de la distance max.
    # Création d'une colonne avec toutes les distances des villes numbeo par rapport au point entré:
    distances = DistanceFromPoint(df, 'lat', 'lon', lat_point, lon_point)
    # Conversion en km
    distances = [i/1000 for i in distances]
    df['distance_km'] = distances
    # Ordre croissant des distances + filtre sur les villes proches en dessous de la distance max:
    df = FiltreSortDf(df, 'distance_km', distance_max)
    
    return df


def VisuSalaires(ville, pays, distance_max, poste):
    """
    Deuxième niveau:
        On reprend la fonction VisuIndex pour obtenir une table triée avec les villes
        de la table numbeo les plus proches d'un point demandé. 
        On va ensuite chercher le salaire (min,moy,max) dans chaque ville numbeo pour le poste demandé.

    Parameters
    ----------
    ville : str, ville de notre choix
    pays : str, pays de la ville.
    distance_max : float| int, distance max entre notre point et ceux de la table numbeo
    poste : str, poste demandé par la personne

    Returns
    -------
    dataframe avec les stats de salaires pour chaque ville proches du point en dessous d'une distance max
    dans la table numbeo.

    """
    # Obtenir le df avec villes proches ordonnées:
    df = VisuIndex(ville, pays, distance_max)
    # Obtenir les salaires (min,moy,max) pour toutes les villes numbeo du df pour le poste demandé:
    df['salaires'] = SalaireNumbeoPoints(df, poste) 
    # la colonne salaires contient des dictionnaires
    # séparation des valeurs des dictionnaires en plusieurs colonnes:
    df = ColDict_toCols(df, 'salaires')
    
    return df

def VisuRatios(ville, pays, distance_max, poste, stat):
    """
    Troisième niveau:
        On veut obtenir salaire(min,maxnmoy)/ indice de cout de la vie.
        On reprend la fonction VisuSalaires pour obtenir les villes proches
        de notre point et les salaires dans ces villes pour un poste donné.
        On calcule ensuite le ratio entre la stat de salaire choisie et l'indice du coût de la vie'

    Parameters
    ----------
    ville : str, ville de notre choix
    pays : str, pays de la ville.
    distance_max : float| int, distance max entre notre point et ceux de la table numbeo
    poste : str, poste demandé par la personne
    stat : str, choix possibles : 'minSal', 'moySal' ou 'maxSal'

    Returns
    -------
    dataframe avec les ratio salaires/indices proches du point demandé pour un poste demandé

    """
    df = VisuSalaires(ville, pays, distance_max, poste)
    # Calcul des ratios pour la stat demandée.
    df = GetRatio(df, stat)
    
    return df

def BarChart():
    # Définir les données pour le graphique
    data = [go.Bar(
        x=['A', 'B', 'C'],
        y=[1, 2, 3]
    )]

    # Créer la figure
    fig = go.Figure(data=data)

    # Afficher le graphique
    fig.show()
    return fig