from fonctionsGen import DistanceFromPoint, FiltreSortDf, ColDict_toCols
from selenium import webdriver
import time
from deep_translator import GoogleTranslator
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import re
# !pip install -U deep-translator

options = webdriver.ChromeOptions()
# options.add_argument('-headless')
options.add_argument('-no-sandbox')
options.add_argument('-disable-dev-shm-usage')
options.add_argument("enable-automation")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(
    "C:/Users/evapa/EVA/ECOLE/ESILV/A5/WEBSCRAPPING/chromium/chromedriver.exe", options=options)

# Variables globales:
lst_idx_vie = ['idx_cout_vie', 'idx_loyer', 'idx_cout_vie_loyer',
               'idx_courses', 'idx_prix_restaurants', 'idx_pouvoir_achat_local']


def EcosiaGlassdoor(poste, localisation):
    driver.get("https://www.ecosia.org/")
    query = 'glassdoor salary {} {}'.format(poste, localisation)
    recherche = driver.find_element_by_xpath(
        "/html/body/div/div/div/div[1]/header/div/form/div/div/div[1]/input")
    recherche.send_keys(query)
    #time.sleep(2)
    recherche.send_keys(Keys.RETURN)
    first_link = driver.find_element_by_xpath(
        "/html/body/div/div/div/main/div[1]/section/div[2]/div[2]/article/div[2]/div[1]/div[2]/a")
    #time.sleep(2)
    first_link.click()
    #time.sleep(2)
    current = driver.current_url
    if current.startswith("https://www.glassdoor"):
        return driver.current_url
    else:
        return None


def ExtractInfoSalary(url_glassdoor):
    driver.get(url_glassdoor)
    #time.sleep(2)
    driver.get(url_glassdoor)
    #time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    minimum = None
    moyenne = None
    maximum = None
    titre_page = None
    localisation_page = None
    if len(soup.find_all('div', class_='d-flex flex-column col')) == 3:
        minimum = soup.find_all(
            'div', class_='d-flex flex-column col')[2].find_all('p')
        if len(minimum) != 0:
            minimum = minimum[0].text
            print('Minimum:', minimum) #retirer
            
            #minimum = [int(i) for i in minimum.split() if i.isdigit()][0]
            minimum = ''.join(re.findall(r'\d', minimum))
            minimum = int(minimum)
            minimum = minimum * 1000

    if soup.find('div', class_='d-flex flex-column align-items-center col') != None:
        moyenne = soup.find(
            'div', class_='d-flex flex-column align-items-center col').find_all('p')
        if len(moyenne) != 0:
            moyenne = moyenne[0].text
            #moyenne = [int(i) for i in moyenne.split() if i.isdigit()][0]
            moyenne = ''.join(re.findall(r'\d', moyenne))
            moyenne = int(moyenne)
            moyenne = moyenne * 1000
    if soup.find('div', class_='d-flex flex-column align-items-end col') != None:
        maximum = soup.find(
            'div', class_='d-flex flex-column align-items-end col').find_all('p')
        if len(maximum) != 0:
            maximum = maximum[0].text
            print('Maximum: ',maximum )
            #maximum = [int(i) for i in maximum.split() if i.isdigit()][0]
            maximum = ''.join(re.findall(r'\d', maximum))
            maximum = int(maximum)
            maximum = maximum * 1000
    if soup.find('h2', class_='d-inline m-0 mr-std careerOverviewNav__CareerOverviewNavStyles__h1') != None:
        titre_page = soup.find(
            'h2', class_='d-inline m-0 mr-std careerOverviewNav__CareerOverviewNavStyles__h1').text
    if soup.find('span', class_='d-inline-flex pt-xxsm mt-0 align-items-center') != None:
        localisation_page = soup.find(
            'span', class_='d-inline-flex pt-xxsm mt-0 align-items-center').text

    if minimum == None and maximum == None and moyenne == None:
        if soup.find('div', class_='row mt-lg') != None:
            moy = soup.find('div', class_='row mt-lg').find_all('span')
            if len(moy) != 0:
                span_els = [el.text for el in moy]
                moyenne = span_els[1].replace(',', '')
                moyenne = [*moyenne]
                moyenne = [int(i) for i in moyenne if i.isdigit()]
                moyenne = int(''.join([str(i) for i in moyenne]))

    return {"minSal": minimum, "moySal": moyenne, "maxSal": maximum, "titrePage": titre_page, "localisationPage": localisation_page}


def formPosteLoc(poste, localisation):
    """
    Fonction qui avec le driver remplit sur glassdor le formulaire
    pour chercher les infos sur salaire pour un poste et une localisation donnés.

    Parameters
    ----------
    poste : TYPE
        DESCRIPTION.
    localisation : TYPE
        DESCRIPTION.


    Returns
    -------
    None.

    """
    #localisation = '{}, {}'.format(ville,pays)
    # Obtenir page salaire
    url_base = "https://www.glassdoor.com/Salaries/index.htm"

    # print('current',driver.current_url)
    driver.get(url_base)
    # Trouver le champ de saisie en utilisant son nom d'attribut "name"
    input_element = driver.find_element_by_name("sc.keyword")

    # Remplir le champ de saisie avec une valeur
    input_element.send_keys(poste)

    location_element = driver.find_element_by_id("LocationSearch")
    time.sleep(4)
    # Remplir le champ de localisation avec une valeur
    location_element.send_keys(localisation)

    # Cliquer sur la loupe pour envoyer le formulaire (poste,localisation)
    button = driver.find_element_by_id("HeroSearchButton")
    button.click()
    time.sleep(5)

    return driver.current_url


def ObtainResultSal(poste, ville, pays):
    localisation = '{}, {}'.format(ville, pays)
    localisation_en = GoogleTranslator(target='en').translate(localisation)
    url_salaires = EcosiaGlassdoor(poste, localisation_en)
    if url_salaires != None:
        dico = ExtractInfoSalary(url_salaires)
        return dico
    else:
        return {'minSal': None, 'moySal': None, 'maxSal': None, 'titrePage': None, 'localisationPage': None}


def SalaireNumbeoPoints(df, poste):
    """

    Parameters
    ----------
    df : un dataframe avec les points triés par distance et avec seulement ceux
    présents dans un périmètre défini par l'utilisateur.
    poste : poste cherché par l'utilisateur

    Returns
    -------
    None.

    """
    # On crée une liste de  salaire en scrappant glassdoor et en prenant la ville et pays contenues dans le df.
    # Cette colonne va contenir un dictionnaire avec salaire moyen, minimum et maximum, et le titre et la localisation trouvée:
    lst_SalairesDico = []
    for index, row in df.iterrows():
        ville = row['ville']
        pays = row['Pays']
        dicoSal = ObtainResultSal(poste, ville, pays)
        lst_SalairesDico.append(dicoSal)
    return lst_SalairesDico


def GetRatio(df, col_salaire):
    """
    Cette fonction permet d'ajouter des colonnes de ratio entre un salaire (minimum, moyen ou maximum)
    et toutes les valeurs d'indices de coût de la vie.
    Parameters
    ----------
    df : dataframe
    col_salaire : colonne contenant soit le salaire minimum, moyen ou maximum.

    Returns
    -------
    df : data frame

    """
    for element in lst_idx_vie:
        new_name = 'ratio_{}_{}'.format(col_salaire, element)
        df[new_name] = df.apply(lambda x: x[col_salaire]/x[element], axis=1)
    return df


# tests:
"""
df = pd.read_csv(
    'C:/Users/evapa/EVA/ECOLE/ESILV/A5/WEBSCRAPPING/projet/projet_webscrapping_padrino_eva_dia3/numbeo/tabAll/tabAllCountries_v3.csv')
res = DistanceFromPoint(df, 'lat', 'lon', -26.20, 28.049)
df['distance_km'] = [i/1000 for i in res]
df = FiltreSortDf(df, 'distance_km', 100)
df['salaire'] = SalaireNumbeoPoints(df, 'Data Scientist')
df = ColDict_toCols(df, 'salaire')
#df = Col
"""

"""
poste = 'Data Scientist'
ville = 'Johannesbourg'
pays = 'Afrique du Sud'
localisation = '{}, {}'.format(ville, pays)
url_salaires = formPosteLoc(poste, localisation)
url_base = "https://www.glassdoor.com/Salaries/index.htm"

if url_base == url_salaires:
    # 1ere méthode traduction en anglais
    localisation_en = GoogleTranslator(target='en').translate(localisation)
    url_salaires = formPosteLoc(poste, localisation_en)
    if url_base == url_salaires:
        # 2eme méthode recherche sur le moteur de recherche Ecosia:
        url_salaires = EcosiaGlassdoor(poste, localisation_en)
    if url_salaires == None:
        print('Pas de réponse pour votre recherche')
if url_salaires!=None:        
    dico = ExtractInfoSalary(url_salaires)
    print(dico)
    
    """

"""
poste = 'Data Scientist'
ville = 'Milan'
pays = 'Italie'
localisation = '{}, {}'.format(ville, pays)
localisation_en = GoogleTranslator(target='en').translate(localisation)
url_salaires= EcosiaGlassdoor(poste, localisation_en)  
if url_salaires != None:
    dico = ExtractInfoSalary(url_salaires)
    print(dico)"""

"""
  
a = EcosiaGlassdoor("Data Scientist", "Johannesbourg, Afrique du Sud")
el=a.find('div',{'class':'d-flex flex-column align-items-center col'})
p=el.find_by_tag_name("p")  """
