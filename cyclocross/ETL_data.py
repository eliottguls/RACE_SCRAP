import requests
import pandas as pd
import json
import psycopg2



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


def get_and_transform_data():
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
                    list_data.append(tr.find_all('td')[0].text + "2023")

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
                    list_data.append(tr.find_all('td')[0].text + "2023")
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



def get_conf(file):
    with open(file, "r") as f:
        return json.load(f)



class ServicePostgres:
    def __init__(self, conf):
        self.conf = conf
        self.db = conf["DB_HOST"]
        self.user = conf["DB_USER"]
        self.password = conf["DB_PASSWORD"]
        self.port = conf["DB_PORT"]
        self.database = conf["DB_NAME"]
    
    def get_connection(self):
        return psycopg2.connect(
            host=self.db,
            user=self.user,
            password=self.password,
            port=self.port,
            database=self.database
        )

    def create_table(self, table_name, columns_list):
        conn = self.get_connection()
        cur = conn.cursor()

        # Ajout du type de données VARCHAR(255) à chaque colonne
        columns_with_types = [f"{column} VARCHAR(255)" for column in columns_list]

        # Concaténation des colonnes avec types
        columns = ", ".join(columns_with_types)

        # Création de la requête SQL complète
        query = f"CREATE TABLE IF NOT EXISTS public.{table_name} ({columns})"

        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()


    def write_pd_to_postgres(self, df, table_name):
        conn = self.get_connection()
        cur = conn.cursor()
        df_columns = list(df)
        columns = ",".join(df_columns)
        values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 
        insert_stmt = "INSERT INTO {} ({}) {}".format(table_name,columns,values)
        cur.executemany(insert_stmt, df.values.tolist())
        conn.commit()
        cur.close()
        conn.close()

    def read_postgres_to_pd(self, query):
        conn = self.get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df


if __name__ == "__main__":
    df = get_and_transform_data()
    conf = get_conf('O:\GET_RACE\conf\conf.json')
    service_postgres = ServicePostgres(conf)
    table_name = "velo_presse_collection_cyclocross"
    service_postgres.create_table(table_name, df.columns.to_list())
    service_postgres.write_pd_to_postgres(df, table_name)