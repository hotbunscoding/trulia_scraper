import sqlite3 as sql
import logging
import csv
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(filename='debug.txt',
                    encoding='utf-8',
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

class DB:

    initialized = False

    def __init__(self):
        self.name = "SQLite 3"

    @classmethod
    def initialize(cls):
        conn = sql.connect('homes.db')
        cursor = conn.cursor()

        if not DB.initialized:
            logging.info("Initializing database and creating table. Please wait...")

            homes = ("CREATE TABLE IF NOT EXISTS Homes ("
                        "Address VARCHAR(125) UNIQUE, "
                        "State VARCHAR(50), "
                        "City VARCHAR(50), "
                        "Zip_Code CHAR(5), "
                        "Link VARCHAR(50) UNIQUE, "
                        "Description VARCHAR(500), "
                        "Beds INTEGER,"
                        "Baths INTEGER,"
                        "Sqft INTEGER,"
                        "Price INTEGER,"
                        "Front_Pic VARCHAR(150),"
                        "Available BOOLEAN,"
                        "Score INTEGER)")

            cursor.execute(homes)
            cursor.close()

            logging.info("Database has been initialized and table has been created. Returning...")
            DB.initialized = True

        return DB.initialized

    @staticmethod
    def write(values: list or dict):
        if not DB.initialized:
            DB.initialize()

        conn = sql.connect('homes.db')
        cursor = conn.cursor()

        query = "INSERT INTO Homes VALUES("

        if isinstance(values, dict):
            last_item = list(values.values())[-1]
            data = []

            for value in values.values():
                query += "?, " if last_item is not value else "?)"
                data.append(str(value) if not isinstance(value, (int, float, bool)) or value is None else value)
            try:
                cursor.execute(query, data)
            except sql.IntegrityError:
                pass


        else:
            last_item = values[-1]

            for value in values.values():
                query += "?, " if last_item != value else "?)"

            try:
                cursor.execute(query, values)
            except sql.IntegrityError:
                pass

        conn.commit()
        cursor.close()

    @staticmethod
    def select(columns: list or str, additional_options: str=""):

        conn = sql.connect('homes.db')
        cursor = conn.cursor()

        if columns == 'all':
            columns = "*"
        else:
            columns = ', '.join(columns)

        returned_data = cursor.execute("SELECT " + columns + " FROM Homes" + additional_options).fetchall()

        cursor.close()
        return returned_data

    @staticmethod
    def custom_query(query):
        conn = sql.connect('homes.db')
        cursor = conn.cursor()
        try:
            cursor.execute(query)
        except sql.Error as e:
            logging.error(e)
            return None

        return cursor.fetchall()

    @staticmethod
    def export_to_csv(city, state):
        print("Exporting data to CSV...")
        date_time = datetime.now().strftime("%m-%d-%y_%H-%M-%S")
        data = DB.select("all", f" WHERE city='{city}' AND state='{state}'")
        columns = ["Address", "State", "City", "Zip Code", "Link", "Description", "Beds", "Baths", "Sqft",
                                 "Price", "Pictures", "Available", "Score"]
        if data:
            with open(f"{city}_{state}_homes_{date_time}.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(data)
        else:
            print(f"Couldn't find any homes in the database in {city}, {state}.\nThis might mean that"
                  f" the city was not found within that given state so "
                  f"Trulia populated homes in the state without having a city selected.\n"
                  f"Exporting results for homes in {state} instead.")

            data = DB.select("all",
                             f" WHERE state='{state}'")

            with open(f"{state}_homes_{date_time}.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(data)
