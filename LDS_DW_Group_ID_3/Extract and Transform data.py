import csv
import requests
from math import ceil, floor
import os
from datetime import datetime 


exchange_rates = dict() 
api_key = '2d5e2d88fc3a120fd7da00bd4fe57bf7'
can_do_requests = True
timeout = 20

#Funzione per salvare i tassi di cambio su un file txt
def save_dict_to_txt(filename):
    with open(filename, 'w') as file:
        for date_currency, rate in exchange_rates.items():
            file.write(f"{date_currency} : {rate}\n")

#Funzione per caricare i tassi di cambio su un file txt
def load_dict_from_txt(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                # Split della riga per ottenere 'data' e 'tasso di scambio'
                date_currency, rate = line.strip().split(' : ')
                exchange_rates[date_currency] = float(rate)
    return 


#Funzione per ottenere i tassi di cambio, a causa del limite di richieste viene fissato per tutto il mese il tasso di cambio del primo del mese
def get_exchange_rate_for_date(year, month, currency):
    if month < 10:
        month_string = '0'+str(month)
    else :
        month_string = str(month)

    try:
        url = f"http://data.fixer.io/api/{str(year)}-{month_string}-01?access_key={api_key}&symbols=USD,CAD,AUD,GBP,NZD"
        response = requests.get(url) 
    
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("Change rate obtained")
                exchange_rates.update({str(year)+str(month)+'EUR' : data['rates']['USD']})
                exchange_rates.update({str(year)+str(month)+'AUD' : data['rates']['USD'] / data['rates']['AUD']})                
                exchange_rates.update({str(year)+str(month)+'CAD' : data['rates']['USD'] / data['rates']['CAD']})
                exchange_rates.update({str(year)+str(month)+'GBP' : data['rates']['USD'] / data['rates']['GBP']})
                exchange_rates.update({str(year)+str(month)+'NZD' : data['rates']['USD'] / data['rates']['NZD']})
                if currency == 'EUR':
                    return data['rates']['USD']  # Restituisce tasso di cambio EUR/USD
                else:
                    return data['rates']['USD'] / data['rates'][currency] # Restituisce tasso di cambio currency/USD
            else:
                print(f"Error in API response: {data.get('error')}")
                if int(data.get("error", {}).get("code")) == 104:  # In caso di errore causato dal raggiungimento limite richieste impedisce richieste future e lo comunica
                    global can_do_requests 
                    can_do_requests = False
                return None
        else:
            print(f"Error in API request: {response.status_code}")
            return None
        
    except requests.exceptions.Timeout:
        # Gestione del timeout
        print(f"Errore: il server ha impiegato troppo tempo a rispondere (timeout impostato: {timeout} secondi)")
        return None
    
    except Exception as e:
        # Gestione di eventuali altre eccezioni
        print(f"Errore imprevisto : {e}")
        return None

#Funzione per estrarre e manipolare i dati dai file
def manipulate_csv_data(input_file_path, input_geo_file_path):
    print(f"Parsing files in tables")

    sales_data = []
    time_data = dict()
    geo_data = dict()

    ram_dict = dict()
    cpu_dict = dict()
    gpu_dict = dict()
    vend_dict = dict()

    country_with_currency = []  # Lista per tenere traccia dei paesi la cui valuta e' stata ottuneta

    cpu_id = 0
    gpu_id = 0
    ram_id = 0  

    size=3412325
    
    # Estrazione dati geografici dal loro file
    with open(input_geo_file_path, mode='r') as file:
        print(f"Parsing Geography file")
        geo_reader = csv.DictReader(file)
        for row in geo_reader:
            geo_data.update({ row['geo_id'] : {
                'geo_id' : row['geo_id'],
                'continent' : row['continent'],
                'country' : row['country'],
                'region' : row['region']
            } })

    # Estrazione dati di vendita dal loro file
    with open(input_file_path, mode='r') as file:
        print(f"Parsing Sales file")
        csv_reader = csv.DictReader(file)

        cpu_id_counter = 0
        ram_id_counter = 0
        gpu_id_counter = 0
        vendor_id_counter = 0

        counter = 0
        percent = 0

        for row in csv_reader:

            # Stampa la percentuale di dati elaborati
            if floor((counter/size)*100) > percent:
                percent+=1
                print(f"Progress = " + str(percent) +"%")
            counter+=1


            # Aggiunge i dati alla tabella delle RAM
            rb = row['ram_brand']
            rn = row['ram_name']
            rs = row['ram_size']
            rt = row['ram_type']
            rc = row['ram_clock']

            ram_key = (rb, rn, rs, rt, rc)
            if ram_key not in ram_dict:
                ram_entry = {
                    'ram_id' : ram_id_counter, 
                    'ram_brand' : rb, 
                    'ram_name' : rn, 
                    'ram_size' : rs, 
                    'ram_type' : rt, 
                    'ram_clock' : rc
                }
                ram_dict[ram_key] = ram_entry
                ram_id_counter += 1
            ram_id = ram_dict[ram_key]['ram_id']   


            # Aggiunge i dati alla tabella delle CPU
            cb = row['cpu_brand']
            cs = row['cpu_series']
            cn = row['cpu_name']
            cnc = row['cpu_n_cores']
            cso = row['cpu_socket']
            
            cpu_key = (cb, cs, cn, cnc, cs)
            if cpu_key not in cpu_dict:
                cpu_entry = {
                    'cpu_id' : cpu_id_counter,
                    'cpu_brand' : cb, 
                    'cpu_series' : cs, 
                    'cpu_name' : cn, 
                    'cpu_n_cores' : cnc, 
                    'cpu_socket' :  cso
                }
                cpu_dict[cpu_key] = cpu_entry
                cpu_id_counter += 1
            cpu_id = cpu_dict[cpu_key]['cpu_id']


            # Aggiunge i dati alla tabella delle GPU
            gb = row['gpu_brand']
            gp = row['gpu_processor']
            gpm = row['gpu_processor_manufacturer']
            gm = row['gpu_memory']
            gmt = row['gpu_memory_type']
            
            gpu_key = (gb, gp, gpm, gm, gmt)
            if gpu_key not in gpu_dict:
                gpu_entry = { 
                    'gpu_id' : gpu_id_counter,
                    'gpu_brand' : gb, 
                    'gpu_processor' : gp, 
                    'gpu_processor_manufacturer' : gpm, 
                    'gpu_memory' : gm, 
                    'gpu_memory_type' : gmt
                }
                gpu_dict[gpu_key] = gpu_entry
                gpu_id_counter += 1
            gpu_id = gpu_dict[gpu_key]['gpu_id']

                
            # Aggiunge i dati alla tabella del tempo
            time = row['time_code']
            year = int(time) // 10000
            month = (int(time) // 100) - (int(year) * 100) 

            if time_data.get(time) is None: 
                day = int(time) % 100
                date = datetime(year, month, day)

                time_data.update({ time : {
                    'time_id' : time,
                    'date' : str(date)[:10],
                    'month': str(date)[:7], 
                    'year' : year,
                    'week' : date.strftime("%W"),
                    'quarter' : 'Q'+ str(ceil(month/3)),                      
                    'day_of_month' : day,
                    'day_of_week' : date.strftime("%A"),
                    'month_of_year' : month,                                        
                    'month_name' : date.strftime("%B")} 
                })

            # Ottiene tasso di cambio per il mese della transazione
            if row['currency'] != 'USD':
                er = exchange_rates.get(str(year)+str(month)+row['currency'])
                if er is not None:
                    exchange_rate = er
                else:
                    if can_do_requests:
                        exchange_rate = get_exchange_rate_for_date(year, month, row['currency'])
                    else:
                        exchange_rate = None
            else:
                exchange_rate = 1

            geo_id = row['geo_id']
            country = geo_data.get(geo_id).get('country')
            if country  not in country_with_currency:
                for entry in geo_data.values():
                    if entry.get('country') == country:
                        entry.update({'currency' : row['currency']})
                country_with_currency.append(country)

            # Aggiunge i dati alla tabella dei venditori
            rvn = row['ram_vendor_name']
            cvn = row['cpu_vendor_name']
            gvn = row['gpu_vendor_name']

            vendors = [rvn, cvn, gvn]
            for vendor in vendors:
                vendor_key = vendor
                if vendor_key not in vend_dict:
                    vendor_entry = { 
                        'vendor_id' : vendor_id_counter,
                        'vendor_name' : vendor_key 
                    }
                    vend_dict[vendor_key] = vendor_entry
                    vendor_id_counter += 1

            ram_vendor_id = vend_dict[rvn]['vendor_id']
            cpu_vendor_id = vend_dict[cvn]['vendor_id']
            gpu_vendor_id = vend_dict[gvn]['vendor_id']


            # Aggiunge i dati alla tabella delle vendite
            sales_entry = {
                'geo_id': geo_id ,
                'time_id': time,
                'ram_id': ram_id,
                'ram_vendor_id' : ram_vendor_id,
                'cpu_id': cpu_id,
                'cpu_vendor_id' : cpu_vendor_id,
                'gpu_id': gpu_id,
                'gpu_vendor_id' : gpu_vendor_id,
                'ram_sales': row['ram_sales_currency'],
                'ram_sales_USD': None,
                'cpu_sales': row['cpu_sales_currency'],
                'cpu_sales_USD': None,
                'gpu_sales': row['gpu_sales_currency'],
                'gpu_sales_USD': None,
                'total_sales': row['sales_currency'],
                'total_sales_USD': None
            }

            
            if exchange_rate is not None:
                sales_entry.update({
                    'ram_sales_USD': str(round(float(row['ram_sales_currency']) * exchange_rate, 2)),
                    'cpu_sales_USD': str(round(float(row['cpu_sales_currency']) * exchange_rate, 2)),
                    'gpu_sales_USD': str(round(float(row['gpu_sales_currency']) * exchange_rate, 2)),
                    'total_sales_USD': str(round(float(row['sales_currency']) * exchange_rate, 2))
                })

            sales_data.append(sales_entry)
        print(f"Progress = 100%")

        return list(ram_dict.values()), list(cpu_dict.values()), list(gpu_dict.values()), list(time_data.values()), list(geo_data.values()), list(vend_dict.values()), sales_data
    
        
# Funzione per salvare i dati in un file csv
def save_dict_to_csv(data_set, filename, fieldnames):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_set:
            writer.writerow(row)

if __name__ == "__main__":

    current_directory = os.path.dirname(os.path.abspath(__file__))
    exchange_rates_file_path = os.path.join(current_directory, 'ex_r.txt')
    input_file_path = os.path.join(current_directory, 'computer_sales.csv')
    input_geo_file_path = os.path.join(current_directory, 'geography.csv')


    # Estrazione e manipolazione dati
    load_dict_from_txt(exchange_rates_file_path)
    try:
        rams_data, cpus_data, gpus_data, time_data, geo_data, vend_data, sales_data = manipulate_csv_data(input_file_path, input_geo_file_path)
    except Exception as e:
            # Gestione di eventuali altre eccezioni
            print(f"Errore imprevisto: {e}")
            save_dict_to_txt(exchange_rates_file_path)  
    save_dict_to_txt(exchange_rates_file_path)

    # Salvataggio dei dati
    save_dict_to_csv(rams_data, os.path.join(current_directory, 'rams_data.csv'), ['ram_id', 'ram_brand', 'ram_name', 'ram_size', 'ram_type', 'ram_clock'])
    save_dict_to_csv(cpus_data, os.path.join(current_directory, 'cpus_data.csv'), ['cpu_id', 'cpu_brand', 'cpu_series', 'cpu_name', 'cpu_n_cores', 'cpu_socket'])
    save_dict_to_csv(gpus_data, os.path.join(current_directory, 'gpus_data.csv'), ['gpu_id', 'gpu_brand', 'gpu_processor', 'gpu_processor_manufacturer', 'gpu_memory', 'gpu_memory_type'])
    save_dict_to_csv(time_data, os.path.join(current_directory, 'time_data.csv'), ['time_id', 'date', 'month', 'year', 'week', 'quarter', 'day_of_month', 'day_of_week', 'month_of_year', 'month_name'])
    save_dict_to_csv(geo_data, os.path.join(current_directory, 'geo_data.csv'), ['geo_id', 'continent', 'country', 'region', 'currency'])
    save_dict_to_csv(vend_data, os.path.join(current_directory, 'vend_data.csv'), ['vendor_id', 'vendor_name'])
    save_dict_to_csv(sales_data, os.path.join(current_directory, 'elaborated_sales_data.csv'),['geo_id', 'time_id', 'ram_id', 'ram_vendor_id', 'cpu_id', 'cpu_vendor_id', 'gpu_id', 'gpu_vendor_id', 'ram_sales', 'ram_sales_USD', 'cpu_sales','cpu_sales_USD', 'gpu_sales', 'gpu_sales_USD', 'total_sales', 'total_sales_USD'])


    # Visualizza il contenuto estratto per verifica
    print(f"Sales Data:", sales_data[:10])
    print(f"CPUs Data:", cpus_data[:10])
    print(f"RAMs Data:", rams_data[:10])
    print(f"GPUs Data:", gpus_data[:10])
    print(f"Time Data:", time_data[:10])
    print(f"Geo Data:", geo_data[:10])
    print(f"Vend Data:", vend_data[:10])



