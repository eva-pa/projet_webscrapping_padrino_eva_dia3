from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd
import os

#### IMPORTS DE FONCTION ####
from fonctionsGen import retirerAccentsListe, getLatLon


# Options du driver Chromium
options = webdriver.ChromeOptions()
options.add_argument('-headless')
options.add_argument('-no-sandbox')
options.add_argument('-disable-dev-shm-usage')
options.add_argument("enable-automation")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome("C:/Users/evapa/EVA/ECOLE/ESILV/A5/WEBSCRAPPING/chromium/chromedriver.exe", options = options)

def getCountryListOnline():
    """
    Fonction pour enregistrer la liste des pays dans un fichier 
    texte dans le dossier numbeo sous le nom de liste_pays.
    Les noms des pays sont changés pour que la création d'URL sur le
    site soit facilitée.

    Returns
    -------
    None.

    """
    # Page principale pour choisir tous les pays
    driver.get('https://fr.numbeo.com/co%C3%BBt-de-la-vie/page-de-d%C3%A9marrage')
    soup=BeautifulSoup(driver.page_source,'html.parser')
    

    # Obtenir la liste de tous les pays disponibles sur le site pour construire les liens pour scrapper les tableaux.
    pays_options = soup.find('div',{'class' :'select_location_form standard_margin'}).find_all('option')[1:]
    pays = [x.text for x in pays_options]
    pays = [x.text.replace(' ','-') for x in pays_options] # on remplace aussi les espaces par des tirets dans les noms pour pouvoir construire les urls par la suite
    # on remplace les accents dans les noms des pays.
    pays = retirerAccentsListe(pays)
    # On retirer les parenthèses
    pays = [x.replace('(','').replace(')','') for x in pays]
    # Enregistrement de cette liste dans un fichier texte
    with open('numbeo/liste_pays.txt', 'w') as f:
        for s in pays:
            f.write(s + '\n')
def GetCountryListFile():
    #Ouverture de la liste de pays disponibles sur numbeo.fr
    with open('numbeo/liste_pays.txt', 'r') as f:
        liste_pays = f.readlines()
        liste_pays = [line.strip() for line in liste_pays]
    return liste_pays

def TabCountryDf(tab_html):
    return 1


"""
driver.close()"""

def GetDf_url(url_pays):
    data = []
    driver.get(url_pays)
    driver.implicitly_wait(10)
    soup=BeautifulSoup(driver.page_source,'html.parser')
    lignes = soup.find('table', {'id': 't2'})
    if lignes:
        lignes=lignes.find_all('tr')
        #print(lignes)
        for ligne in lignes:
            if ligne.find_all('td'):
                #print([element.text for element in ligne.find_all('td')])
                data.append([element.text for element in ligne.find_all('td')])
                df = pd.DataFrame(data, columns = ['classement','ville','idx_cout_vie','idx_loyer','idx_cout_vie_loyer','idx_courses','idx_prix_restaurants','idx_pouvoir_achat_local'])
                df['Pays']=soup.find('input', {'name': 'locCountry'})['value']
    else: 
        return -1
    return df

def is_integer(x):
  if isinstance(x, int):
    return True
  else:
    return False


def SaveTabsCountry():
    liste_pays = GetCountryListFile()
    url_tab_base = 'https://fr.numbeo.com/co%C3%BBt-de-la-vie/pays/{}'
    urls_tabs = [url_tab_base.format(x) for x in liste_pays]
    #urls_tabs = [url_tab_base.format('France')] # test a retirer
    
    for pays in liste_pays:
        url = url_tab_base.format(pays)
        df = GetDf_url(url)
        
        if isinstance(df,int)==False:
            path = os.getcwd()
            filename = '{}\\numbeo\\tableaux_pays\\{}.csv'.format(path,pays)
            
            df.to_csv(filename)
            
def AddCoordinatesDf(df,col_city,col_country):
    df['lat']= None
    df['lon']=None
    #df[['lat','lon']] = df.apply(lambda x: getLatLon(x[col_city], x[col_country]),axis=1)
    #df['col_3'] = df.apply(lambda x: f(x.col_1, x.col_2), axis=1)
    latitudes = []
    longitudes = []
    for index, row in df.iterrows():
     lat, lon = getLatLon(row[col_city],row[col_country])
     latitudes.append(lat)
     longitudes.append(lon)
    df['lat'] = latitudes
    df['lon'] = longitudes
    return df


def SaveOneTab():
    path = os.getcwd()
    directory = '{}\\numbeo\\tableaux_pays'.format(path)
    lst_dfs = []
    for filename in os.listdir(directory):
        open_path = '{}\\{}'.format(directory,filename)
        df = pd.read_csv(open_path)
        lst_dfs.append(df)
    
    df_final = pd.concat(lst_dfs)
    
    #sauvegarde du dataframe avec toutes les lignes de tous les tableaux par pays
    df_final = df_final
    path_save_file = '{}\\numbeo\\tabAll\\tabAllCountries.csv'.format(path)
    df_final.to_csv(path_save_file)
    return df_final

def modifTabAllV2():
    """
    Quelques modifications sur le dataframe contenant tous les pays.
    Et sauvegarde de ce nouveau dataset

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    path = os.getcwd()
    directory = '{}\\numbeo\\tabAll\\tabAllCountries.csv'.format(path)
    df = pd.read_csv(directory)
    # changer Taiwan (Chine) par Taiwan dans la colonne pays
    #df[df.Pays=='Taïwan (Chine)']['Pays'] = 'Taïwan'
    df.loc[df['Pays'] == 'Taïwan (Chine)', 'Pays'] = 'Taïwan'
    
    df = AddCoordinatesDf(df, 'ville', 'Pays')
    
    dir_final = '{}\\numbeo\\tabAll\\tabAllCountries_v2.csv'.format(path)
    df.to_csv(dir_final)
    return df

def modifCoordinatesV2():
    path = os.getcwd()
    directory = '{}\\numbeo\\tabAll\\tabAllCountries_v2.csv'.format(path)
    df = pd.read_csv(directory)
    #Quebec City
    df.loc[ df["ville"] =="La ville de Québec (existing value)", "lat"] = 46.81213588141209
    df.loc[ df["ville"] =="La ville de Québec (existing value)", "lon"] = -71.22480805636772
    # Puebla Mexique:
    df.loc[ df["ville"] =="Puebla", "lat"] = 19.029972893272678
    df.loc[ df["ville"] =="Puebla", "lon"] = -98.2108382512503
    # Ciudad de Mexico au Mexique
    df.loc[ df["ville"] =="Mexico", "lat"] = 19.4326296
    df.loc[ df["ville"] =="Mexico", "lon"] = -99.1331785
    # Brasilia au Brésil
    df.loc[ df["ville"] =="Brasilia", "lat"] = -15.7934036
    df.loc[ df["ville"] =="Brasilia", "lon"] = -47.8823172
    # Ajdir (Al Hoceïma) au Maroc
    df.loc[ df["ville"] =="Ajdir (Al Hoceïma)", "lat"] = 35.24585232196229
    df.loc[ df["ville"] =="Ajdir (Al Hoceïma)", "lon"] = -3.9336508363095124
    # Zoug en Suisse
    df.loc[ df["ville"] =="Zoug", "lat"] = 47.16721239749653
    df.loc[ df["ville"] =="Zoug", "lon"] = 8.515408091291068
    # Bergame en Italie
    df.loc[ df["ville"] =="Bergame", "lat"] = 45.6937582592198
    df.loc[ df["ville"] =="Bergame", "lon"] = 9.669262467441616
    # Brescia en Italie
    df.loc[ df["ville"] =="Brescia", "lat"] = 45.53788582687871 
    df.loc[ df["ville"] =="Brescia", "lon"] = 10.213862655436365
    
    dir_final = '{}\\numbeo\\tabAll\\tabAllCountries_v2.csv'.format(path)
    df.to_csv(dir_final)
    return df    

def modifTabV3():
    path = os.getcwd()
    directory = '{}\\numbeo\\tabAll\\tabAllCountries_v2.csv'.format(path)
    df = pd.read_csv(directory)
    lst_idx_vie = ['idx_cout_vie', 'idx_loyer', 'idx_cout_vie_loyer', 'idx_courses', 'idx_prix_restaurants','idx_pouvoir_achat_local']
    # On remplace les virgules par des points
    for idx_cout in lst_idx_vie:
        df[idx_cout]= df[idx_cout].apply(lambda x: x.replace(',','.'))
        df[idx_cout] = df[idx_cout].astype('float')
    dir_final = '{}\\numbeo\\tabAll\\tabAllCountries_v3.csv'.format(path)
    df.to_csv(dir_final)
    return df
    
"""
Latitude et longitude à corriger:
Quebec (city) Canada
Puebla Mexique
Mexico Mexico (=Ciudad de Mexico)
Brasilia Brasil
Maroc Ajdir (Al Hoceïma)
Zoug/Zug en suisse
Bergame / Bergamo en Italie
Brescia Italie
"""
   
def testFunct(col_a, col_b):
    return 1,2
        
# Fonctions lancées pour tout obtenir
# GetCountryListOnline()
# SaveTabsCountry()
#SaveOneTab()
#modifTabAllV2()
#modifCoordinatesV2()
#modifTabV3()
#driver.close()


#Données pour lancer test
#df = getDf_Url('https://fr.numbeo.com/co%C3%BBt-de-la-vie/pays/Kosovo-territoire-conteste')