"""
Choisissez n'importe quelle page Produit sur le site de Books to Scrape. Écrivez un script Python qui visite cette page et en extrait les informations suivantes :

product_page_url
universal_product_code
title
price_including_tax
price_excluding_tax
number_available
product_description
category
review_rating
image_url

Écrivez les données dans un fichier CSV qui utilise les champs ci-dessus comme en-têtes de colonnes.
Maintenant que vous avez obtenu les informations concernant un premier livre, vous pouvez essayer de récupérer toutes les données nécessaires pour toute une catégorie d'ouvrages. Choisissez n'importe quelle catégorie sur le site de Books to Scrape. Écrivez un script Python qui consulte la page de la catégorie choisie, et extrait l'URL de la page Produit de chaque livre appartenant à cette catégorie. Combinez cela avec le travail que vous avez déjà effectué afin d'extraire les données produit de tous les livres de la catégorie choisie, puis écrivez les données dans un seul fichier CSV.
Remarque : certaines pages de catégorie comptent plus de 20 livres, qui sont donc répartis sur différentes pages («  pagination  »). Votre application doit être capable de parcourir automatiquement les multiples pages si présentes. 
Ensuite, étendez votre travail à l'écriture d'un script qui consulte le site de Books to Scrape, extrait toutes les catégories de livres disponibles, puis extrait les informations produit de tous les livres appartenant à toutes les différentes catégories, ce serait fantastique  ! Vous devrez écrire les données dans un fichier CSV distinct pour chaque catégorie de livres.
Enfin, prolongez votre travail existant pour télécharger et enregistrer le fichier image de chaque page Produit que vous consultez  !
Au cours du projet, veillez à enregistrer votre code dans un repository GitHub
"""

import requests
import csv
from bs4 import BeautifulSoup

#Cette méthode permet de recuperer la liste des url des catégories
def run_main_page_for_categories_url_to_scrap(main_url):
	dictionary_categories = dict()
	response = requests.get(main_url)
	#Testons le code retour pour éviter une page KO
	if response.status_code !=200:
		print("error "+response.status_code)
	else:
		main_page = requests.get(main_url)
		main_soup = BeautifulSoup(main_page.content, 'html.parser')
		# Ciblons la section du menu à gauche
		main_soup = main_soup.find(class_="nav nav-list")
		# Ciblons la balise <a href
		for url in main_soup.find_all("a", href=True):
			#Recuperons le nom de la catégorie
			name_category = url.string
			#Le retour est visiblement rempli d'espace à neutraliser
			name_category = name_category.lstrip()
			name_category = name_category.rstrip()
			#récupérons l'url relative et ajoutons le nom de domaine
			url_category = main_url+url['href']
			#print(name_category)
			#print(url_category)
			
			#Le tête de liste Books est un retour à la liste globale. On ignore
			if(name_category != "Books"):
				#on enregistre dans un dictionnaire nom/categorie
				dictionary_categories[name_category] = url_category
	#print(dictionary_categories)
	return dictionary_categories

"""We will scrap each category collecting book's url
def run_all_categories_collect_book_url(categories_url_list):
	books_url_list = []
	for category_url in categories_url_list:
		books_url_list.append(collect_book_url_from_category_page(category_url))
	return books_url_list
"""

#Cette méthode va récuperer pour chaque catégorie la liste des pages livres en parcourant si besoin les pages suivantes
def scrap_a_category_page_for_url(category_url):
	url_list=[]
	category_page = requests.get(category_url)
	category_soup = BeautifulSoup(page.content, 'html.parser')

	#
	# url_list.append(soup.find_all("td", class_="pb-2 font-600 text-sm xs:text-base sm:text-lg leading-tight pt-2"))
	#

	if(collect_url_from_next_button(category_url) is not None):
		url_list.append(scrap_a_category_page_for_url(collect_category_page_from_next_button(category_url)))

	return url_list

#Cette méthode renvoie l'url de la page next ou none s'il n'y en a pas
def collect_category_page_from_next_button (page_url):
	if (thereisanextbutton):
		return next_url
	else:
		return None


#Scrap a book/product into a dictionnary	
def scrap_a_book_file(book_url):
	
	book_page = requests.get(book_url)
	book_soup = BeautifulSoup(page.content, 'html.parser')
	book_soup.find_all("td", class_="pb-2 font-600 text-sm xs:text-base sm:text-lg leading-tight pt-2")
	print(book_url)

	dictionary_booktoscrape = dict()
	dictionary_booktoscrape["product_page_url"] = ""
	dictionary_booktoscrape["universal_product_code"] = ""
	dictionary_booktoscrape["title"] = ""
	dictionary_booktoscrape["price_including_tax"] = ""
	dictionary_booktoscrape["price_excluding_tax"] = ""
	dictionary_booktoscrape["number_available"] = ""
	dictionary_booktoscrape["product_description"] = ""
	dictionary_booktoscrape["category"] = ""
	dictionary_booktoscrape["review_rating"] = ""
	dictionary_booktoscrape["image_url"] = ""

	return dictionary_booktoscrape

#création d'un nouveau fichier pour une catégorie
def create_new_category_csv(category):
# La liste des en-têtes
	en_tete = ["product_page_url","universal_product_code","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]

	# Créer un nouveau fichier pour écrire dans le fichier csv du nom de la catégorie
	with open(category+'.csv', 'w') as category_csv:
		# Créer un objet writer (écriture) avec ce fichier
		writer = csv.writer(category_csv, delimiter=',')
		writer.writerow(en_tete)
	return category_csv

def write_in_category_csv(fichier_csv, dictionary_booktoscrape):
	writer = csv.writer(fichier_csv, delimiter=',')
   	
   	# Parcourir les titres et descriptions - zip permet d'itérer sur deux listes ou plus à la fois
	for item in dictionary_booktoscrape:
		print(item)
      	# Créer une nouvelle ligne avec les items
      	#ligne = [titre, description]
    #writer.writerow(ligne)
	return fichier_csv

#Notre URL de travail
main_url = "http://books.toscrape.com/"

#Récupérons un dictionnaire de Nom/Url de toutes les catégories
categories_list = run_main_page_for_categories_url_to_scrap(main_url)

#Bouclons sur la liste
for category in categories_list:
	
	#créons un nouveau fichier csv. L'objectif est d'en créer un pour chacune
	category_csv = create_new_category_csv(category)

	#Récupérons la liste des urls de tous les livres de la catégorie 
	print(categories_list[category])
'''
	book_list = scrap_a_category_page_for_url(categories_list[category])
	print(book_list)

	for book_url in book_urls:
		print(scrap_a_book_file(book_url))
		#write_in_category_csv(category_csv)
'''
