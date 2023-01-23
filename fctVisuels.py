from fonctionsGen import getLatLon, DistanceFromPoint, FiltreSortDf, ColDict_toCols
from glassdoorscrap import SalaireNumbeoPoints, GetRatio, ObtainResultSal
import os
import pandas as pd
import plotly.graph_objs as go
import folium
from folium.features import DivIcon
from IPython.display import display

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

def x_axis_title(col1,col2, col3):
    return '{}, {}, {} km'.format(col1, col2, round(col3,2))

def BarChart(df, indice, order = False, stat = None, option_ratio = False):
    # indice peut être none pour juste afficher les salaires
    df['locComplete'] = df[['ville','Pays','distance_km']].apply(lambda x : x_axis_title(*x), axis = 1)
    x_col = 'locComplete'
    if stat == None and option_ratio == False:
        y_col = indice
    if stat != None and option_ratio == False:
        y_col = stat
    if stat!= None and option_ratio == True:
        y_col = 'ratio_{}_{}'.format(stat, indice)

    
    data = [go.Bar(
        x=df[x_col],
        y= df[y_col],
        text= round(df[y_col],2),
        textposition='auto'
    )]
    fig = go.Figure(data=data)
    if order == True:
        fig.update_layout(xaxis={'categoryorder':'total descending'})
    return fig




def afficherBar(ville, pays, distance_max,indice, poste, salaireStat, ratio, ordre_valeurs,lancerProgramme=False):
    if lancerProgramme == True:
        # premier niveau
        if poste == '' and salaireStat == None:
            df_Visu = VisuIndex(ville,pays,distance_max)
            fig = BarChart(df=df_Visu,indice=indice,order=ordre_valeurs)
            fig.update_layout(title="Graphique à barres des valeurs d'indices de {} dans un rayon de {} km".format(indice, distance_max),
                  xaxis_title="Villes et distances par rapport à {}, {}".format(ville, pays),
                  yaxis_title="Valeur de l'indice {}".format(indice))
            fig.show()
        if poste !='' and salaireStat != None and ratio == False:
            df_Visu = VisuSalaires(ville, pays, distance_max, poste)
            fig = BarChart(df=df_Visu,indice=indice, stat = salaireStat,order=ordre_valeurs,option_ratio=ratio)
            fig.update_layout(title="Graphique à barres des salaires sur la statistique {} pour le poste {} dans un rayon de {} km".format(salaireStat, poste, distance_max),
                  xaxis_title="Villes et distances par rapport à {}, {}".format(ville, pays),
                  yaxis_title="Valeur de {} pour le poste de {}".format(salaireStat, poste))
            fig.show()
        if poste !='' and salaireStat != None and ratio == True:
            df_Visu = VisuRatios(ville,pays,distance_max,poste,salaireStat)
            fig = BarChart(df=df_Visu,indice=indice,order=ordre_valeurs,stat=salaireStat,option_ratio=ratio)
            fig.update_layout(title="Graphique à barres des ratios entre la statistique de salaire {} et l'indice {} pour le poste {} dans un rayon de {} km".format(salaireStat, indice, poste, distance_max),
                  xaxis_title="Villes et distances par rapport à {}, {}".format(ville, pays),
                  yaxis_title="Valeur du ratio entre {} et {} pour le poste de {}".format(salaireStat, indice, poste))
            fig.show()
            
def afficherCarte(ville, pays, distance_max,indice, poste, salaireStat, ratio,lancerProgramme=False):
    if lancerProgramme == True:
        df_Visu = 0
        lat_point, lon_point = getLatLon(ville, pays)
        if poste == '' and salaireStat == None:
            df_Visu = VisuIndex(ville,pays,distance_max)
            colAffichage = indice
        if poste !='' and salaireStat != None and ratio == False:
            df_Visu = VisuSalaires(ville, pays, distance_max, poste)
            colAffichage = salaireStat
        if poste !='' and salaireStat != None and ratio == True:
            df_Visu = VisuRatios(ville,pays,distance_max,poste,salaireStat)
            colAffichage = 'ratio_{}_{}'.format(salaireStat,indice)
        if df_Visu.shape[0]!=0:
            m = folium.Map([float(lat_point), float(lon_point)], zoom_start=5)
            for ville_df in df_Visu.ville.unique():
                latitude = df_Visu[df_Visu['ville']==ville_df]['lat'].iloc[0]
                longitude = df_Visu[df_Visu['ville']==ville_df]['lon'].iloc[0]
                text = round(df_Visu[df_Visu['ville']==ville_df][colAffichage].iloc[0],2)
                folium.map.Marker([latitude, longitude],icon_size=(50,16),popup=ville).add_to(m)
                folium.map.Marker([latitude+ 0.05, longitude - 0.05], icon= DivIcon(icon_size=(150,36),icon_anchor=(0,0),html='<div style="font-size: 11pt;background: white; width: 30px">%s</div>' % text,)).add_to(m)
            folium.map.Marker([lat_point, lon_point],icon_size=(50,16),popup=ville).add_to(m)
            display(m)
            return m            