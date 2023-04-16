#importing modules

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import re
import math
import os
import psycopg2

#downloading the regional prefixes' list, e.g. SPB.move.ru, MSK.move.ru

reg = pd.read_excel('reg_prefixes.xlsx')

options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)

#connecting to the SQL database
connection = psycopg2.connect(database="move_sell", user="postgres", password="kworb1791!",
                              host="127.0.0.1", port="5432")

connection.autocommit = True
cursor = connection.cursor()

#downloading the list of previously collected links so that we do not download them once again
cursor.execute('SELECT * FROM links')
result = cursor.fetchall()
ready_links = [x[0].split('_')[-1][:-1] for x in result]

"""
cursor.execute('SELECT * FROM links_january')
result = cursor.fetchall()
for y in result:
    ready_links.append(y[0].split('_')[-1][:-1])
"""
limit = 100

counter = 0
results_list = []
regions_list = []
i = 0

#launching a cycle
while i<len(reg):
    try:
        region = reg.loc[i]["Регион"]
        if region != 'Москва':
            if len(reg.loc[i]["Префикс"].split("/")) == 2:
                if len(reg.loc[i]["Префикс"].split("/")[0]) < 1:
                    first_pref = ''
                    second_pref = '/' + reg.loc[i]["Префикс"].split("/")[1]
                else:
                    first_pref = reg.loc[i]["Префикс"].split("/")[0] + '.'
                    second_pref = '/' + reg.loc[i]["Префикс"].split("/")[1]
            elif len(reg.loc[i]["Префикс"].split("/")) == 1:
                 first_pref = reg.loc[i]["Префикс"] + '.'
                 second_pref = ''
            else:
                first_pref = ''
                second_pref = '/'
        else:
            first_pref = ''
            second_pref = ''
        link = f'https://{first_pref}move.ru{second_pref}/kommercheskaya_nedvijimost/'
        driver.get(link)
        page_text = driver.find_element(By.TAG_NAME, 'html').text
        total_listings = int(re.findall('\nВсего .{1,} объявлен', page_text)[0].replace('\nВсего', '').replace('объявлен', '').replace(' ', ''))
        total_pages = math.ceil(total_listings/limit)
        page = 1
        while page<=total_pages:
            query = link + f'?page={page}&limit={limit}'
            driver.get(query)
            links = driver.find_elements(By.CLASS_NAME, 'search-item__item-link')
            for result in links:
                if result.get_attribute('href') not in results_list:
                    #link_dict = {'link': result.get_attribute('href'), 'region': region}
                    regions_list.append(region)
                    results_list.append(result.get_attribute('href').split('_')[-1])
                    counter += 1
                    print(i, counter)
                #else: continue
            page += 1
    except Exception as e: print(region, 0, e)
    i += 1
driver.quit()

dx = pd.DataFrame()

dx['links'] = results_list
dx['regions'] = regions_list

dx.to_excel('move_sell_links_march.xlsx')

dx = dx.drop_duplicates().reset_index().drop('index', axis=1)

#downloading the data into the SQL database
j = 0
while j < len(dx):
    if dx.loc[j]['links'][:-1] not in ready_links:
        cursor.execute(f"INSERT INTO links_march VALUES ('{dx.loc[j]['links'][:-1]}', '{dx.loc[j]['regions']}')")
    j += 1
  
connection.close()