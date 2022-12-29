from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from bs4 import BeautifulSoup

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

# Page principale pour choisir tous les pays
driver.get('https://fr.numbeo.com/co%C3%BBt-de-la-vie/page-de-d%C3%A9marrage')
soup=BeautifulSoup(driver.page_source,'html.parser')


# Obtenir la liste de tous les pays disponibles sur le site pour construire les liens pour scrapper les tableaux.
pays_options = soup.find('div',{'class' :'select_location_form standard_margin'}).find_all('option')[1:]
pays = [x.text for x in pays_options]
pays = [x.text.replace(' ','-') for x in pays_options] # on remplace aussi les espaces par des tirets dans les noms pour pouvoir construire les urls par la suite

# Enregistrement de cette liste dans un fichier texte
with open('numbeo/liste_pays.txt', 'w') as f:
  for s in pays:
    f.write(s + '\n')

#Ouverture de la liste de pays disponibles sur numbeo.fr
with open('numbeo/liste_pays.txt', 'r') as f:
  liste_pays = f.readlines()
  liste_pays = [line.strip() for line in liste_pays]

# construction des urls
url_tableau_base = 'https://fr.numbeo.com/co%C3%BBt-de-la-vie/pays/{}'
urls_tableaux = [url_tableau_base.format(x) for x in liste_pays]


driver.close()