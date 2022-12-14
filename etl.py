import requests
import csv
import os
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

#Cette méthode permet de recuperer la liste des url des catégories
def run_main_page_for_categories_url_to_scrap(main_url):
	dictionary_categories = dict()
	response = requests.get(main_url)
	#Testons le code retour pour éviter une page KO
	if response.status_code !=200:
		print("error "+response.status_code)
	else:
		#On utilise la bibliotheque d'analyse synthaxique BeautifulSoup
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

#Cette méthode va récuperer pour chaque catégorie la liste des pages livres en parcourant si besoin les pages suivantes
def scrap_a_category_page_for_url(category_url):
	url_list=[]

	category_page = requests.get(category_url)
	category_soup = BeautifulSoup(category_page.content, 'html.parser')
	# Ciblons la section centrale
	category_soup = category_soup.find(class_="col-sm-8 col-md-9")
	
	# Ciblons les images qui contiennent l'url. On évite le doublon avec le lien texte
	for url in category_soup.find_all("div", class_="image_container"):
		#on recupere l'url
		url_book = url.find("a", href=True)
		url_book = url_book['href']
		
		#L'url est relative. Il faut recréer l'url absolu avec un urljoin
		url_book = urljoin(category_url,url_book)
		
		#On ajoute l'url collectée au fichier retourné
		url_list.append(url_book)
			
	next_url = collect_following_category_url_from_next_button(category_url)

	if(next_url is not None):
		#print("dans le if next " + next_url)
		#on utilise cette même fonction pour boucler sur toutes les pages suivantes
		scrap_a_category_page_for_url(next_url)
	
	#print(url_list)
	return url_list

#Cette méthode renvoie l'url de la page next ou none s'il n'y en a pas
def collect_following_category_url_from_next_button (category_url):

	category_page = requests.get(category_url)

	category_soup = BeautifulSoup(category_page.content, 'html.parser')
	# Ciblons le bouton Next pour en extraire l'url
	next_soup = category_soup.find(class_="next")
	# On doit sortir avec un résultat none en l'absence de bouton next
	if(next_soup is None):
		return None
	else:
		#on recupere l'url
		next_url = next_soup.find("a", href=True)
		#L'url est relative. On utilise à nouveau urljoin itsmagic
		next_url = urljoin(category_url,next_url['href'])
		return next_url


#Scrap a book/product into a dictionnary	
def scrap_a_book_file(book_url, category, information_list):
	dictionary_booktoscrape = dict()
	
	#L'url et la catégorie sont disponibles directement depuis les arguments de notre fonction
	dictionary_booktoscrape[information_list[0]] = book_url
	dictionary_booktoscrape[information_list[7]] = category

	book_page = requests.get(book_url)
	book_soup = BeautifulSoup(book_page.content, 'html.parser')

	#Une partie des informations est disponibles dans le tableau table-striped
	product_table = book_soup.find(class_="table table-striped")
	product_table = product_table.find_all("td")
	dictionary_booktoscrape[information_list[1]] = product_table[0].string
	dictionary_booktoscrape[information_list[4]] = product_table[2].string
	dictionary_booktoscrape[information_list[3]] = product_table[3].string
	
	#Le cas du stock est particulier. Il serait préférable de récupérer une valeur entier en supprimant texte et parenthèses 
	string_stock = product_table[5].string
	if(string_stock.startswith("In stock")):
		string_stock = string_stock.replace("In stock (","")
		string_stock = string_stock.replace(" available)","")
	#On va également gérer le cas qui ne commencent pas en In Stock comme un valeur à 0 
	else:
		string_stock = "0"
	dictionary_booktoscrape[information_list[5]] = string_stock

	#La Partie ProductMain contient plusieurs informations à récupérer
	main_soup = book_soup.find(class_="col-sm-6 product_main")
	title_soup = main_soup.find("h1")
	dictionary_booktoscrape[information_list[2]] = title_soup.string

	#On va récuperer la note sous forme d'entier en vérifiant la présence de la star-rating class
	if(main_soup.find(class_="star-rating One") is not None):
		review_rating = 1
	elif(main_soup.find(class_="star-rating Two") is not None):
		review_rating = 2
	elif(main_soup.find(class_="star-rating Three") is not None):
		review_rating = 3
	elif(main_soup.find(class_="star-rating Four") is not None):
		review_rating = 4
	elif(main_soup.find(class_="star-rating Five") is not None):
		review_rating = 5
	else: 
		#Pour maintenir l'idée d'avoir un entier, on choisira le code erreur -1
		review_rating = -1
	
	dictionary_booktoscrape[information_list[8]] = review_rating

	#Ciblons l'élément carousel qui contient un tag <img> dont src est l'url
	carousel_soup = book_soup.find(class_="carousel-inner")
	carousel_soup = carousel_soup.find("img", src=True)
	#Comme toujours, ne pas oublier de transformer l'url relative en absolue avec la fonction urljoin
	dictionary_booktoscrape[information_list[9]] = urljoin(book_url,carousel_soup['src'])

	#Récuperons la Product Description
	#Il n'y pas vraiment d'accroche. C'est un <p> au milieu de nul part. On va cibler le sub-header et utiliser l'élément suivant de même imbrication
	product_soup = book_soup.find(class_="sub-header")
	product_soup = product_soup.find_next_sibling()
	
	dictionary_booktoscrape[information_list[6]] = product_soup.string

	return dictionary_booktoscrape

#création d'un nouveau fichier pour une catégorie
def create_new_category_csv(category, information_list, folder_name):
# La liste des en-têtes
	
	# Créer un nouveau fichier pour écrire dans le fichier csv du nom de la catégorie
	# l'attribut newline = '' permet d'éviter des sauts de lignes
	# Vu la ponctuation présente dans la description, on choisit le delimiter |
	with open(f"{folder_name}/{category}.csv", 'w', encoding='utf-8', newline='') as category_csv:
		# Créer un objet writer (écriture) avec ce fichier
		writer = csv.writer(category_csv, delimiter='|')
		writer.writerow(information_list)
	return category_csv

def write_in_category_csv(fichier_csv, dictionary_booktoscrape, information_list, folder_name):
	# Créons une nouvelle ligne.
	row = []

	#On va boucler sur notre fichier entete pour s'assurer que tout changement d'ordre sera repercuté
	for information in information_list:
		row.append(dictionary_booktoscrape[information])		

	#Ajoutons la ligne au fichier .csv ouvert en mode append 'a'
	# l'attribut newline = '' permet d'éviter des sauts de lignes
	# l'attribut encoding utf-8 corrige l'erreur 'charmap' codec can't encode character '\ufb01'
	with open(fichier_csv.name, 'a', encoding='utf-8', newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter='|')
		writer.writerow(row)		
	return fichier_csv

def download_image(book_scrapped, folder_name):
	response = requests.get(book_scrapped[information_list[9]]).content
	
	with open(f"{folder_name}/{book_scrapped[information_list[1]]}.jpg", "wb+") as f:
		f.write(response)
	
def image_folder_create():
    
    try:
        folder_name = input("Nom du dossier pour le téléchargement des images:- ")
        # folder creation
        os.mkdir(folder_name)
        print("Dossier "+folder_name+" créé avec succès")
        return folder_name

    # if folder exists with that name, ask another name
    except:
        print("Ce dossier existe déjà !")
        return folder_name
        #On peut ici forcer un nouveau dossier inexistant
        #image_folder_create()

def csv_folder_create():
    
    try:
        folder_name = input("Nom du dossier pour le téléchargement des données en csv:- ")
        # folder creation
        os.mkdir(folder_name)
        print("Dossier "+folder_name+" créé avec succès")
        return folder_name

    # if folder exists with that name, ask another name
    except:
        print("Ce dossier existe déjà !")
        return folder_name
        #On peut ici forcer un nouveau dossier inexistant
        #image_folder_create()

#Notre URL de travail
main_url = "http://books.toscrape.com/"

#les informations attendues
information_list = ["product_page_url","universal_product_code","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]

#L'utilisateur peut choisir les noms de dossiers pour stocker csv et images
folder_image = image_folder_create()
folder_csv = csv_folder_create()

#C'est parti pour le scrapping
start = time.time()
loop_count = 0

#Récupérons un dictionnaire de Nom/Url de toutes les catégories
categories_list = run_main_page_for_categories_url_to_scrap(main_url)

#Bouclons sur la liste
for category in categories_list:
	print("==> Début de la Catégorie "+category)
	#créons un nouveau fichier csv. L'objectif est d'en créer un pour chacune
	category_csv = create_new_category_csv(category, information_list, folder_csv)

	#Récupérons la liste des urls de tous les livres de la catégorie 
	book_list = scrap_a_category_page_for_url(categories_list[category])
	
	#On va maintenant boucler notre liste d'url. Ici nous sommes dans une catégorie, et donc son csv associé
	for book_url in book_list:
		#On effectue le web scapping de la page livre
		book_scrapped = scrap_a_book_file(book_url, category, information_list)
		#On enregistre l'image
		download_image(book_scrapped, folder_image)
		#On ajoute la ligne au CSV
		category_csv = write_in_category_csv(category_csv, book_scrapped, information_list, folder_csv)
		loop_count +=1
		
		#Notre retour console
		retour = "> Enregistrement #"+str(loop_count)+" : "
		if (len(book_scrapped[information_list[2]])>50):

			retour += book_scrapped[information_list[2]][0:49]
		else:
			retour += book_scrapped[information_list[2]]
		
		print(retour)

#Le Scrapping est terminé
total_time = time.time() - start
print("===> Opération terminée. Merci <===")
print(">"+str(loop_count)+ " pages parcourues en "+ str(int(total_time/60))+" minute(s) et "+str(int(total_time%60))+" seconde(s)")