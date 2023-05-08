#importing modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
from datetime import datetime, date, timedelta
import pandas as pd
import os
import math

#setting options
options = Options()
options.add_argument("--headless")

reg_prefixes = pd.read_excel('etagi_regions.xlsx')
driver = webdriver.Chrome(options=options)

#listings_list = []

import psycopg2

#connecting to our SQL database
connection = psycopg2.connect(database="etagi_sell", user="postgres", password="kworb1791!",
                              host="127.0.0.1", port="5432")

cursor = connection.cursor()

#launching the cycle
i = 0
listings_list = []
while i < len(reg_prefixes):
    driver.get(f'https://{reg_prefixes.loc[i]["Префикс"]}.etagi.com/commerce/')
    try:
        pages = int(math.ceil(int(driver.find_elements(By.CLASS_NAME, 'col-3')[0].text.split()[1])/30))
        for page in range(1, pages+1):
            driver.get(f'https://{reg_prefixes.loc[i]["Префикс"]}.etagi.com/commerce/?page={page}')
            page_source = driver.page_source        
            data = re.findall('var data=.{1,}etagi.com"}}}</script>', page_source)
            result = eval(data[0].replace('var data=', '').replace('</script>', '').replace('false', ' False').replace('true', ' True').replace('null', ' None'))
            listings = result['lists']['commerce']    
            for listing in listings:
                if listing['action_sl'] == 'sale':
                    listing_dict = {}
                    listing_dict['ID'] = str(listing['object_id'])
                    listing_dict['Адрес'] = f'{listing["meta"]["city"]}, {listing["meta"]["street"]}, {listing["house_num"]}'
                    listing_dict['Цена'] = float(listing['price'])
                    listing_dict['Цена за м²'] = float(listing['price_m2'])
                    listing_dict['Площадь'] = float(listing['square'])
                    listing_dict['Регион'] = reg_prefixes.loc[i]["Регион"]
                    test = f"SELECT * FROM links WHERE ID='{listing_dict['ID']}'"
                    test2 = f"SELECT * FROM links_january WHERE ID='{listing_dict['ID']}'"
                    cursor.execute(test)
                    r = cursor.fetchall()
                    cursor.execute(test2)
                    r2 = cursor.fetchall()
                    if len(r) == 0:
                        f = 'да'
                        listing_dict['4кв 2022'] = 'да'
                    else:
                        f = '-'
                        listing_dict['4кв 2022'] = 'нет'
                    if len(r2) == 0:
                        s = 'да'
                        listing_dict['1кв 2023'] = 'да'
                    else:
                        s = '-'
                        listing_dict['1кв 2023'] = 'нет'
                    sql = f'''INSERT INTO links_may VALUES ('{listing_dict['ID']}', '{listing_dict['Адрес']}', {listing_dict['Цена']}, {listing_dict['Цена за м²']}, {listing_dict['Площадь']}, '{listing_dict['Регион']}', '{f}', '{s}')'''
                    cursor.execute(sql)
                    connection.commit()
                    listings_list.append(listing_dict)
    except Exception as err: print(err, reg_prefixes.loc[i]["Префикс"])
    print(i)
    i += 1

driver.quit()   
connection.close()

listings_df = {
    'ID': [],
    'Адрес': [],
    'Цена': [],
    'Цена за м²': [],
    'Площадь': [],
    'Регион': [],
    '4кв 2022': [],
    '1кв 2023': []
    }

for x in listings_list:
    for key in x:
        listings_df[key].append(x[key])
        
df = pd.DataFrame(listings_df)

df.to_excel('etagi_rent_links_may_1.xlsx')