from selenium import webdriver
import time
from deep_translator import GoogleTranslator
# !pip install -U deep-translator
 
options = webdriver.ChromeOptions()
#options.add_argument('-headless')
options.add_argument('-no-sandbox')
options.add_argument('-disable-dev-shm-usage')
options.add_argument("enable-automation")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-extensions")
options.add_argument("--dns-prefetch-disable")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome("C:/Users/evapa/EVA/ECOLE/ESILV/A5/WEBSCRAPPING/chromium/chromedriver.exe", options = options)

def EcosiaGlassdoor():
    
def formPosteLoc(poste,localisation):
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
    #Obtenir page salaire
    url_base = "https://www.glassdoor.com/Salaries/index.htm"
    
    #print('current',driver.current_url)
    driver.get(url_base)
    # Trouver le champ de saisie en utilisant son nom d'attribut "name"
    input_element = driver.find_element_by_name("sc.keyword")
    
    # Remplir le champ de saisie avec une valeur
    input_element.send_keys(poste)
    
    location_element = driver.find_element_by_id("LocationSearch")
    
    # Remplir le champ de localisation avec une valeur
    location_element.send_keys(localisation)
    
    #Cliquer sur la loupe pour envoyer le formulaire (poste,localisation)
    button = driver.find_element_by_id("HeroSearchButton")
    button.click()
    time.sleep(5)
    
    return driver.current_url

poste = 'Data Scientist'
ville = 'Johannesbourg'
pays = 'Afrique du Sud'
localisation = '{}, {}'.format(ville,pays)
url_salaires = formPosteLoc(poste, localisation)
url_base = "https://www.glassdoor.com/Salaries/index.htm"
if url_base == url_salaires:
    # 1ere méthode traduction en anglais 
    localisation_en = GoogleTranslator(target='en').translate(localisation)
    url_salaires = formPosteLoc(poste, localisation_en)
    if url_base == url_salaires:
        # 2eme méthode recherche sur le moteur de recherche Ecosia:
            
    
    # Si l'addresse est la même on change la ville et le pays en anglais.
    #data['avis_en'] = data['avis'].apply(lambda x: GoogleTranslator(source='fr', target='en').translate(x))
    
