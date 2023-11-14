import requests
import pandas as pd

from bs4 import BeautifulSoup
from urllib.parse import urljoin



def get_all_url_calendar(discipline):
    # URL de la page web que vous souhaitez scraper
    base_url = f'https://velopressecollection.ouest-france.fr/{discipline}/calendrier/'


    session = requests.Session()

    # Envoyer une requête GET pour récupérer le contenu HTML de la page
    response = requests.get(base_url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Parser le contenu HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraire les liens de la page
        links = soup.find_all('a')

        # Extraire les liens avec le même nom de domaine que la page de départ
        domain_links = [urljoin(base_url, link.get('href')) for link in links if urljoin(
            base_url, link.get('href')).startswith(base_url)]

        #Enlever le tr entier si le 3 td est égale à 'Championnats de France\xa0'
        for tr in soup.find_all('tr'):
            if tr.find_all('td')[2].text == 'Championnats de France\xa0':
                tr.decompose()
        
        # Faire un nouveau tableau qui ne contient que les liens ou le mot calendrier est présent 2 fois et que chaque lien soit unique et il ne faut pas qu'il ya it le mot championnat dans le lien
        url = []
        for i in range(len(domain_links)):
            if domain_links[i].count('calendrier') == 2 and domain_links[i] not in url and 'championnat' not in domain_links[i]:
                url.append(domain_links[i])
        url.sort()
        return url
    else:
        print(f"Échec de la requête : {response.status_code}")
        return None


def et_data():
    # Get all url
    url = get_all_url_calendar('cyclo-cross')

    # Create a dataframe with column : date, name, category, 'champ', infos, club, dept
    df_data = pd.DataFrame(columns=['date', 'name', 'category', 'champ', 'infos', 'club', 'dept'])


    # Envoyer une requête GET pour récupérer le contenu HTML de la page
    for i in range(len(url)):

        response = requests.get(url[i])
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Parser le contenu HTML avec BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extraire le mois et l'année
            month = soup.find('h1').text.split(' ')[0]
            year = soup.find('h1').text.split(' ')[1]

            # the html code of the calendar is right after the first h2 tag of page
            soup = soup.find('h2').find_next_sibling()

            # last td tag of eahc tr tag must be 22 or 29 or 35 or 56
            for tr in soup.find_all('tr'):
                if tr.find_all('td')[-1].text not in ['22', '29', '35', '56']:
                    tr.decompose()

            # ignore tr if the 3 td tag has strong tag in and "ANNULÉ" value
            for tr in soup.find_all('tr'):
                if tr.find_all('td')[2].find('strong') != None or tr.find_all('td')[2].text == 'ANNULÉ':
                    tr.decompose()




            # récupérer la date de la course qui est le premier td pour chaque tr
            for tr in soup.find_all('tr'):
                list_data = []
                if tr.find_all('td')[0].text == ' ':
                    list_data.append('No date for now')
                else:
                    list_data.append(tr.find_all('td')[0].text)

                if tr.find_all('td')[1].text == ' ':
                    list_data.append('No race name for now')
                else:
                    list_data.append(tr.find_all('td')[1].text)

                if tr.find_all('td')[2].text == ' ':
                    list_data.append('No category for now')
                else:
                    list_data.append(tr.find_all('td')[2].text)

                # si tr.find_all('td')[3].text contient au moins la chaine de caractère "Championnat" 
                if 'Championnat' in tr.find_all('td')[3].text:
                    list_data.append(tr.find_all('td')[3].text)

                    # si dans le tr.find_all('td')[4] il y a <p> qui est son enfant
                    if tr.find_all('td')[4].text == ' ':
                        list_data.append("No infos for now")
                    elif tr.find_all('td')[4].find('p') != None:
                        list_data.append("https://velopressecollection.ouest-france.fr" + tr.find_all('td')[4].find('p').find('a').get('href'))
                    elif tr.find_all('td')[4].find('p') == None:
                        list_data.append("https://velopressecollection.ouest-france.fr" + tr.find_all('td')[4].find('a').get('href'))


                    if tr.find_all('td')[5].text == ' ':
                        list_data.append('No club for now')
                    else:
                        list_data.append(tr.find_all('td')[5].text)

                    if tr.find_all('td')[6].text == ' ':
                        list_data.append('No dept for now')
                    else:
                        list_data.append(tr.find_all('td')[6].text)
                else:
                    if tr.find_all('td')[3].text == ' ':
                        list_data.append('No champ for now')
                    else:
                        list_data.append(tr.find_all('td')[3].text)

                    if tr.find_all('td')[4].text == ' ':
                        list_data.append("No infos for now")
                    else:
                        list_data.append("https://velopressecollection.ouest-france.fr" + tr.find_all('td')[4].find('a').get('href'))
                    if tr.find_all('td')[5].text == ' ':
                        list_data.append('No club for now')
                    else:
                        list_data.append(tr.find_all('td')[5].text)
                try:
                    if len(list_data) == 6:
                        list_data.append(tr.find_all('td')[6].text)
                except:

                    list_data = []
                    list_data.append(tr.find_all('td')[0].text)
                    list_data.append(tr.find_all('td')[1].text)
                    list_data.append("No cat for now")
                    list_data.append(tr.find_all('td')[2].text)
                    list_data.append("https://velopressecollection.ouest-france.fr" + tr.find_all('td')[3].find('a').get('href'))
                    if tr.find_all('td')[4].text == ' ':
                        list_data.append("No club for now")
                    else:
                        list_data.append(tr.find_all('td')[4].text)
                    list_data.append(tr.find_all('td')[5].text)
                    
                #Ajouter a df_data les valeurs
                df_data.loc[len(df_data)] = list_data
        else:
            print(f"Échec de la requête : {response.status_code}")
    return df_data


if __name__ == "__main__":
    df_data = et_data()
    df_data.to_csv('df_data.csv', index=False)
    print(df_data)