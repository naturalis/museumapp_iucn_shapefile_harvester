import sqlite3

class Database:

    DATABASE = 'downloads.db3'

    def __init__(self):
        self.conn = sqlite3.connect(self.DATABASE)
        self.cursor = self.conn.cursor()
        self.create_table()


    def __del__(self):
        self.conn.commit()
        self.conn.close()


    def create_table(self):
        self.cursor.execute('''CREATE TABLE if not exists iucn_download_requests (taxon varchar, synonym varchar, request_date datetime)''')
        self.cursor.execute('''CREATE TABLE if not exists iucn_downloads (taxon varchar primary key, download_date datetime, search_date datetime)''')


    def save_download_request(self,taxon,request_date,synonym=None):
        self.cursor.execute(
            "INSERT into iucn_download_requests (taxon, request_date, synonym) VALUES (?,?,?)",
            [taxon,request_date,synonym]
        )

    def get_download_requests(self):
        self.cursor.execute("select * from iucn_download_requests")
        return self.cursor.fetchall()

    def get_downloads(self):
        self.cursor.execute("select * from iucn_downloads")
        return self.cursor.fetchall()

    def save_download(self,taxon,download_date,search_date):
        self.cursor.execute(
            "INSERT or replace into iucn_downloads (taxon, download_date, search_date) VALUES (?,?,?)",
            [taxon,download_date,search_date]
        )

    def get_synonyms(self):
        self.cursor.execute("select distinct taxon,synonym from iucn_download_requests where synonym is not null")
        return self.cursor.fetchall()

