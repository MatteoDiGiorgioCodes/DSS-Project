import pandas as pd
import os
from sqlalchemy import create_engine


#Connessione al DB
server = '131.114.72.230' 
database = 'GROUP_ID_3_DB' 
username = 'Group_ID_3' 
password = '13SZ34S4' 
connectionString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
print(f"Connection to server")
connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(connection_string)
print(f"Connected to server")

    
# Funzione per popolare le tabelle
def populate_table(data_path, table):
    df = pd.read_csv(data_path)
    print(f"Populating {table} table")
    df.to_sql(table, con=engine, if_exists='append', index=False)


# Popolare tutte le tabelle
if __name__ == "__main__":

    current_directory = os.path.dirname(os.path.abspath(__file__))

    try:
        populate_table(os.path.join(current_directory, 'cpus_data.csv'), 'Cpu')
        populate_table(os.path.join(current_directory, 'rams_data.csv'), 'Ram')
        populate_table(os.path.join(current_directory, 'gpus_data.csv'), 'Gpu')
        populate_table(os.path.join(current_directory, 'time_data.csv') , 'Time')
        populate_table(os.path.join(current_directory, 'geo_data.csv'), 'Geography')
        populate_table(os.path.join(current_directory, 'vend_data.csv'), 'Vendors')
        populate_table(os.path.join(current_directory, 'elaborated_sales_data.csv'), 'Computer_sales')
    except Exception as e:
            print(f"Errore imprevisto: {e}")
    print(f"Loading complete")
