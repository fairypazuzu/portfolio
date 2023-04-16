# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 01:23:19 2023

@author: p.ignatenok
"""
#modules' import
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import re
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import textwrap
#import pymongo
import pandas as pd
#import nextcloud_client
import os

options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)

calendar = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
    }

office_types = {
    'офис': 'Офис',
    'склад': 'Склад',
    'пп': 'Производственное помещение',
    'псн': 'Помещение свободного назначения',
    'псу': 'Помещение сферы услуг',
    'осз': 'Отдельно стоящее здание',
    'гостиница': 'Гостиница',
    'нежилое здание': 'Нежилое здание',
    'тп': 'Торговое помещение'
    }
#building function for dates

def know_time(string_time):
    parts = string_time.split(' ')
    for part in parts:
        if ':' in part:
            parts.remove(part)
    if 'в' in parts:
        parts.remove('в')
    if parts[0] == 'сегодня':
        return str(date.today())
    if parts[0] == 'вчера':
        return str(date.today()-timedelta(days=1))
    if len(parts)==2:
        if len(str(parts[0]))==1:
            return str(datetime.strptime(f'0{parts[0]}/{calendar[parts[1]]}/2022', '%d/%m/%Y').date())
        else: return str(datetime.strptime(f'{parts[0]}/{calendar[parts[1]]}/2022', '%d/%m/%Y').date())
    else:
        if len(str(parts[0]))==1:
            return str(datetime.strptime(f'0{parts[0]}/{calendar[parts[1]]}/{parts[2]}', '%d/%m/%Y').date())
        else: return str(datetime.strptime(f'{parts[0]}/{calendar[parts[1]]}/{parts[2]}', '%d/%m/%Y').date())

errors = []
errors_reg = []



#loading pre-parsed list of links (id numbers of listing on move.ru)
docs_list = pd.read_excel('C:/').drop('Unnamed: 0', axis=1)
docs_list = docs_list.rename(columns={'error_link': 'links', 'error_region': 'regions'})

#launching a cycle
i = 0

while i < len(docs_list):
    query = tuple(docs_list.loc[i])
    try:
        driver.get(f'https://move.ru/objects/{query[0]}')
        #getting source and text of a listing's page
        page_source = driver.page_source
        page_text = driver.find_elements(By.TAG_NAME, 'html')[0].text
        if 'Данный объект продан' not in page_text:
            listing_dict = {}
            items = driver.find_elements(By.CLASS_NAME, 'object-info__details-table_property_name')
            items_values = driver.find_elements(By.CLASS_NAME, 'object-info__details-table_property_value')
            for item in items:
                if item.text.startswith('г. ') or item.text.startswith('м. '):
                    break
                else: listing_dict[f'{item.text[:-1]}'] = ''
            v_c = 0
            for value in items_values[:len(listing_dict)]:
                listing_dict.update({list(dict.keys(listing_dict))[v_c]: value.text})
                v_c += 1
            listing_dict['Период аренды'] = listing_dict['Цена'].split(' в ')[1]
            if 'Площадь участка'  in list(dict.keys(listing_dict)):
                if (listing_dict['Площадь участка'].split()[1] == 'га') or (listing_dict['Площадь участка'].split()[1] == 'гектар'):
                    listing_dict['Площадь участка'] = float(listing_dict['Площадь участка'].split()[0])*100
                else: listing_dict['Площадь участка'] = float(listing_dict['Площадь участка'].split()[0])
            else: listing_dict['Площадь участка'] = '-'
            for currency in ['₽', '$', '€']:
                try:
                    listing_dict['Цена'] = int(listing_dict['Цена'].split(' в ')[0].replace(' ', '').replace(currency, ''))
                    listing_dict['Валюта'] = currency
                    break
                except: print('ok')                
            #listing_dict['Общая площадь'] = float(listing_dict['Общая площадь'].replace(' ', '').replace('м²', ''))
            listing_dict['Дата публикации'] = know_time(listing_dict['Дата публикации'])
            if 'Дата обновления' in list(dict.keys(listing_dict)):
                listing_dict['Дата обновления'] = know_time(listing_dict['Дата обновления'])
            else:
                listing_dict['Дата обновления'] = '-'
            listing_dict['ID'] = listing_dict['ID'].replace('-', '')
            listing_dict['Ссылка'] = f'https://move.ru/objects/{query[0]}'
            listing_dict['Источник'] = 'move'
            listing_dict['Адрес'] = re.findall(';YaMaps.address=".{1,}";YaMaps.', page_source)[0].replace(';YaMaps.address="', '').replace('";YaMaps.', '')  
            if 'Тип объекта' in list(dict.keys(listing_dict)):
                try:
                    listing_dict['Тип объекта'] = office_types[listing_dict['Тип объекта']]
                except: listing_dict['Тип объекта'] = listing_dict['Тип объекта']
            else:
                listing_dict['Тип объекта'] = '-'
            try:
                coords = re.findall(';YaMaps.coords=\[.{1,}\];YaMaps.zoom', page_source)[0].replace(';YaMaps.coords=[', '').replace('];YaMaps.zoom', '')
                listing_dict['Широта'] = float(coords.split(', ')[0])
                listing_dict['Долгота'] = float(coords.split(', ')[1])
                listing_dict['гео позиция'] = coords.split(', ')[0] + ' ' + coords.split(', ')[1]
            except:
                listing_dict['Широта'] = '-'
                listing_dict['Долгота'] = '-'
                listing_dict['гео позиция'] = '-'        
            listing_dict['Текст'] = driver.find_elements(By.CLASS_NAME, 'object-page__text-block')[0].text
            try:
                listing_dict['Агент'] = driver.find_elements(By.XPATH, '//div[@class="block-user__name"]')[0].text
            except: listing_dict['Агент'] = '-'
            try:
                listing_dict['Контакт агента'] = driver.find_elements(By.XPATH, '//a[@class="block-user__name"]')[0].get_attribute('href')
            except: listing_dict['Контакт агента'] = '-'
            try:
                listing_dict['Организация'] = driver.find_elements(By.XPATH, '//div[@class="block-user__agency"]')[0].text
            except: listing_dict['Организация'] = '-'
            listing_dict['Дата скачивания'] = str(datetime.now().date())
            if 'Комиссия агенту' not in list(dict.keys(listing_dict)):
                listing_dict['Комиссия агенту'] = '-'
            if 'Этаж' in list(dict.keys(listing_dict)):
                if '/' in listing_dict['Этаж']:
                    floors = listing_dict['Этаж'].split('/')
                    listing_dict['Этаж'] = int(floors[0])
                    listing_dict['Этажей в здании'] = int(floors[1])
                else:
                    listing_dict['Этаж'] = int(listing_dict['Этаж'])
                    listing_dict['Этажей в здании'] = int(listing_dict['Этаж'])
            else:
                listing_dict['Этаж'] = '-'
                listing_dict['Этажей в здании'] = '-'
            if 'Количество комнат' in list(dict.keys(listing_dict)):
                listing_dict['Количество комнат'] = int(listing_dict['Количество комнат'])
            listing_dict['Подкатегория'] = 'Аренда'
            listing_dict['Регион'] = query[1]
            #listing_dict['Прошлый ключ'] = docs_list.loc[i]['key']
            images = driver.find_elements(By.TAG_NAME, 'img')
            nec_images = []
            for image in images:
                if image.get_attribute('src') != None:
                    nec_images.append(image.get_attribute('src'))
            nec_images_x = '['
            for l in nec_images:
                if '.jp' in l and listing_dict['ID'] in l:
                    nec_images_x += f'{l}, '
            if len(nec_images_x) == 1:
                nec_images_x += ']'
            else: nec_images_x = nec_images_x[:-2] + ']'
            listing_dict['Ссылки на фото'] = nec_images_x
            ds = re.findall('\nИнформация\n.{1,}\nНайти схожие объявления', page_text)
            if len(ds)>0:
                description = ds[0].split('\n')[2]
            else:
                description = 'Данный объект продан'
            listing_dict['Описание'] = description
            """
            listing_dict['Цена за сотку'] = listing_dict['Цена']/listing_dict['Площадь участка']
            for xx in ['цена за сотку', 'Цена за га', 'цена за га']:
                if xx in list(listing_dict.keys()):
                    del listing_dict[xx]
            """
            if '' in list(listing_dict.keys()):               
                del listing_dict['']
            if 'цена за м²' in list(listing_dict.keys()): 
                del listing_dict['цена за м²']
            #since all data items are collected, we can write down a file that can be processed later
            with open(f'D:/move_data_rent_jan/{listing_dict["ID"]}.txt', 'w', encoding='utf-8') as f:
                f.write(str(listing_dict))
                f.close()
            
            #making a screenshot
            total_width = 779
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(total_width, total_height)
            driver.save_screenshot('page_image2.png')
            im = Image.open('page_image2.png')
            #for a header
            img = Image.new('RGB', (im.size[0], 120), color = (132, 207, 255))
            fnt = ImageFont.truetype('Roboto-Black.ttf', 18)
            d = ImageDraw.Draw(img)
            lines = textwrap.wrap(f'ССЫЛКА: {listing_dict["Ссылка"]}', width=70)
            h = 10
            for line in lines:
                d.text((10,h), line, font=fnt, fill=(0, 0, 0))
                h += 18
            d.text((10,h+30), f'ДАТА СКАЧИВАНИЯ: {datetime.now()}', font=fnt, fill=(0, 0, 0))
            #img.save('header_image.png')
            merged_image = Image.new('RGB', (im.size[0], im.size[1]+img.size[1]), color = (255, 255, 255))
            merged_image.paste(img, (0, 0))
            merged_image.paste(im, (0, img.size[1]))
            
            try:
                merged_image.save(f'Z:/move_screenshots/{listing_dict["ID"][:3]}/{listing_dict["ID"][3:6]}/{listing_dict["ID"]}.jpg')
            except:
                if f'{listing_dict["ID"][:3]}' not in os.listdir('Z:/move_screenshots'):
                    os.mkdir(f'Z:/move_screenshots/{listing_dict["ID"][:3]}/')
                if f'{listing_dict["ID"][3:6]}' not in os.listdir(f'Z:/move_screenshots/{listing_dict["ID"][:3]}'):
                    os.mkdir(f'Z:/move_screenshots/{listing_dict["ID"][:3]}/{listing_dict["ID"][3:6]}')
                    merged_image.save(f'Z:/move_screenshots/{listing_dict["ID"][:3]}/{listing_dict["ID"][3:6]}/{listing_dict["ID"]}.jpg')
                else: merged_image.save(f'Z:/move_screenshots/{listing_dict["ID"][:3]}/{listing_dict["ID"][3:6]}/{listing_dict["ID"]}.jpg')
            #nc.put_file(f'./move_screenshots_sell_land/{listing_dict["ID"]}.jpg', './send_file.jpg')
            
        else: print(i, 'Продан')        
    except Exception as err:
        errors.append(docs_list.loc[i]['links'])
        errors_reg.append(docs_list.loc[i]['regions'])
        print(err, len(errors))
    print(i)
    i += 1
 


driver.quit()
df = pd.DataFrame()
df['error_link'] = errors
df['error_region'] = errors_reg
df.to_excel('move_errors_rent_jan_12.xlsx')