import pandas as pd
import psycopg2
import json

from google.auth.transport.requests import Request

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

    def read_postgres_to_pd(self, query):
        conn = self.get_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df

def get_config():
    with open("C:\Users\eliot\OneDrive - Université de Rennes 1\Bureau\GET_RACE\conf\conf.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":
    conf = get_config()
    service_postgres = ServicePostgres(conf)
    query = "SELECT * FROM public.velo_presse_collection_cyclocross"
    df = service_postgres.read_postgres_to_pd(query)

    print(df.head())