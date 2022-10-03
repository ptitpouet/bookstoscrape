# bookstoscrape
Projet 2 - Utilisez les bases de Python pour l'analyse de marché
https://github.com/ptitpouet/bookstoscrape.git
Auteur : Thierry Moncorger pour Openclassrooms.com

### Présentation

J'ai utilisé Python 3.10 et le logiciel SublimeText comme outil de développement.
Merci de consulter [requirements.txt](requirements.txt) pour les specifications de 
platforme, python et packages nécessaires. Il nécessite un terminal connecté à Internet.

Ce projet est un script de Web-scrapping du site Books to Scrape (http://books.toscrape.com/ ). 

Dans l'environnment virtuel conforme à [requirements.txt](requirements.txt) le script s'éxécute via la commande suivante ans le dossier contenant le script
# python etl.py

### Pré-requis

l'url de travail qui est propre à ce script (main_url = "http://books.toscrape.com/") et la liste des informations à extraires (information_list = ["product_page_url","universal_product_code","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]) sont des informations constantes et propriété de ce script.

La console permet de suivre le parcours de chaque catégorie, livre à livre
Un message ainsi qu'un compteur final renseignent sur le nombre de livres enregistrés et le temps total d'éxécution du script.

Les fichiers images suivent la nomenclature suivante :
universal_product_code . jpg
L'utilisateur peut donc relier chaque ligne produit au fichier image correspondant. L'url source de l'image contenu dans le csv permet de ne pas perdre l'origine du fichier.

Les fichiers csv utilisent le formatage de fichier 'utf-8'. Le script renvoie un fichier csv par catégorie. La nomenclature est le nom de catégorie (.csv) récupéré lors du parcours de celles-ci
Le séparateur est le caractère "|". Il est à noter que les descriptions des produits contiennent de nombreux ";" et "," rendant sensible le choix de ces caractères comme séparateurs (pour la concersion de données sur excel par exemple).


### Déroulé du script

0 - L'utilisateur est invité à choisir le nom pour le dossier qui contiendra les images téléchargées puis l'utilisateur est invité à choisir le nom pour le dossier qui contiendra les csv des données des livres de chaque catégorie 

1 - Le script va parcourir le menu des catégories et retourner une liste sous forme de dictionnaire {Nom de la Catégorie} : {url de la catégorie}

2 - On va boucler la liste des catégories une à une

2.1 - Pour chaque catégorie, on créé le fichier {titre de la catégorie}.csv dans le dossier nommé par l'utilisateur avec les champs de information_list comme en-têtes de colonnes.
2.2 - On récupère une liste de chaque url de produit (la fiche descriptive de chaque livre)
2.3 - On détecte une éventuelle pagination via la présence d'un lien texte 'next'. Le cas échéant on relance la méthode avec l'url récupérée du lien texte

3 - On parcours la liste des urls de produit avec une méthode permettant le scrapping des éléments de la fiche descriptive et qui renvoie un dictionnaire {information} en clé : {données recupérées} en valeur.

3.1 - A chaque passage de la boucle des urls de produit, on ajoute la ligne dans le csv de la catégorie parcourue

3.2 - A chaque passage de la boucle des urls de produit, on télécharge l'image depuis l'url du dictionnaire retoruné en - 3

3.3 - Un print console permet de suivre le parcours de chaque catégorie, livre à livre.

4 - A la fin du parcours de tous les produits de chaque catégorie. La console indique le nombre d'enregistrements et le temps total d'éxécution.

### Utilisation des données

Les données sont désormais prêtes à être exploitées via un tableur type excel, en utilisant le séparateur défini (|) ou peuvent être importées dans une base de données via l'importation de csv. La première ligne correspondant aux en-têtes de colonnes.
Rappel : Les fichiers du dossier images (le nom est défini par l'utilisateur) sont associables à chaque ligne de produit par l'utilisateur de la clé valeur unique universal_product_code (.jpg)