import requests

# URL de la page web que vous souhaitez scraper
url = 'https://www.example.com'

# Envoyer une requête GET pour récupérer le contenu HTML de la page
response = requests.get(url)

# Vérifier si la requête a réussi
if response.status_code == 200:
    # Récupérer le contenu HTML de la page entière
    page_content = response.text

    # Vous pouvez maintenant traiter page_content selon vos besoins
    # par exemple, enregistrer le contenu dans un fichier ou le traiter pour extraire des informations spécifiques.

else:
    print(f"Échec de la requête : {response.status_code}")
