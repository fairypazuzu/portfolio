#importing modules

import pandas as pd
import os

listings_list = []

directory = 'D:/'
files = os.listdir(directory)


i = 0
errors = []

#collecting pre-parsed data
for file in files:
    #try:
        with open(directory+file, 'r', encoding='utf-8') as f:
            listing = f.read()
            if 'selenium' not in listing:
                listings_list.append(eval(listing.replace('ObjectId', '')))
            else: errors.append(file)
            f.close()
    #except: continue
        print('download', i)
        i += 1


#list of all the columns that may appear in a txt file of a building
columns = ['Цена',
 'Тип объекта',
 'Тип объявления',
 'Площадь участка',
 'Дата публикации',
 'Дата обновления',
 'ID',
 'Валюта',
 'Ссылка',
 'Адрес',
 'Широта',
 'Долгота',
 'гео позиция',
 'Текст',
 'Агент',
 'Контакт агента',
 'Организация',
 'Дата скачивания',
 'Комиссия агенту',
 'Этаж',
 'Этажей в здании',
 'Подкатегория',
 'Регион',
 'Ссылки на фото',
 'Описание',
 'Цена за сотку',
 'Свободная планировка',
 'Водопровод',
 'Электричество',
 'Газ',
 'Возможен торг',
 'Количество этажей',
 'Канализация',
 'Online-показ',
 'Новостройка',
 'Охрана',
 'Управляющая компания',
 'Год постройки',
 'Количество подъездов',
 'Серия',
 'Тип дома',
 'Количество жилых помещений',
 'Тип фундамента',
 'Тип перекрытия',
 'Количество комнат',
 'Тип здания',
 'Застройщик',
 'Детская площадка',
 'Жилая площадь',
 'цена за м²',
 'Общая площадь',
 'Отопление',
 'Площадь кухни',
 'Наименьшее количество этажей',
 'Наибольшее количество этажей',
 'Баня/сауна',
 'п. Усть-Ордынский (центр)']

problem_columns = {
    'бизнес-цент': 'Бизнес-центр',
    'Тип объект': 'Тип объекта',
    'Класс Б': 'Класс',
    'Стату': 'Статус',
    'Общая площад': 'Общая площадь',
    'Этажност': 'Этажность',
    'Год постройк': 'Год постройки',
    'Тип помещени': 'Тип помещения',
    'Парковк': 'Парковка',
    'Высота потолко': 'Высота потолков',
    'Площадь офисо': 'Площадь офисов',
    'Количество помещени': 'Количество помещений',
    'Тип планирово': 'Тип планировок',
    'Арендная площад': 'Арендная площадь',
    'Год реконструкци': 'Год реконструкции',
    'Дата публикации': 'Опубликовано',
    'Дата обновления': 'Обновлено'} 

office_types = {
    'офис': 'Офисное помещение',
    'склад': 'Склад',
    'пп': 'Производственное помещение',
    'псн': 'Помещение свободного назначения',
    'псу': 'Помещение сферы услуг',
    'осз': 'Отдельно стоящее здание',
    'гостиница': 'Гостиница',
    'нежилое здание': 'Нежилое здание',
    'тп': 'Торговое помещение',
    'отп': 'Отдельное маленькое помещение'
    }

float_columns = ['Общая площадь', 'Площадь участка', 'Арендная площадь',
                 'Жилая площадь', 'Высота потолков', 'Площадь кухни']
int_columns = ['Этаж', 'Этажей в здании', 'Количество этажей', 'Количество комнат',
               'Количество подъездов', 'Год постройки',
               'Наименьшее количество этажей', 'Наибольшее количество этажей',
               'Количество жилых помещений', 'Год реконструкции',
               'Количество корпусов', 'Количество квартир', 'Этажность']


#building a list of listings, correcting possible mistakes from the previous step
listings = []
i = 1
for doc in listings_list:
    listing_dict = {}
    for key in doc:
        if key in problem_columns:
            if key == 'Тип объект':
                try:
                    listing_dict[problem_columns[key]] = office_types[doc[key]]
                except: listing_dict[problem_columns[key]] = doc[key]
            else: listing_dict[problem_columns[key]] = doc[key]
        else: listing_dict[key] = doc[key]
    if 'Валюта' not in listing_dict:
        listing_dict['Валюта'] = '₽'
    for k in listing_dict:
        if k in float_columns:
            try:
                listing_dict[k] = float(listing_dict[k].replace(',', '.').replace(' ', '').replace('м', '').replace('²', ''))
            except: listing_dict[k] = doc[k]
        elif k in int_columns:
            try:
                listing_dict[k] = int(listing_dict[k])
            except: listing_dict[k] = listing_dict[k]
        else: listing_dict[k] = listing_dict[k]
    listings.append(listing_dict)
    #print(i)
    i += 1

cols = []

for listing in listings:
    for c in list(listing.keys()):
        if c not in cols:
            cols.append(c)

listings_out = []
for ltng in listings:
    for cl in cols:
        if cl not in list(ltng.keys()):
            ltng[cl] = '-'
    listings_out.append(ltng)

lens = []
lens_dict = {}

for l in listings_out:
    if len(l) not in lens:
        lens.append(len(l))
        lens_dict.update({len(l): 1})
    else: lens_dict[len(l)] += 1


df_dict = {}
for cl in cols:
    df_dict.update({cl: []})
    
for l in listings_out:
    for key in l:
        df_dict[key].append(l[key])
        
df = pd.DataFrame(df_dict)

items = pd.read_excel('items.xls')

items_dict = {}
i = 0
while i < len(items):
    items_dict.update({items.loc[i]['Объект']: [items.loc[i]['Значение'], items.loc[i]['Колонка']]})
    i += 1


#we need to assign buildings to previously elaborated categories 
categories = pd.read_excel('cats.xlsx')

cat_dict = {}
i = 0
while i < len(categories):
    cat_dict.update({categories.loc[i]['list']: [categories.loc[i]['cat'], categories.loc[i]['sub'], categories.loc[i]['func']]})
    i += 1


import re

types = []
sqs = []
ii = 0
while ii < len(df):
    t = re.findall('Продается .{1,} площадью', df.loc[ii]['Описание'])
    if len(t) > 0:
        types.append(t[0].replace('Продается ', '').replace(' площадью', ''))
    else: types.append(df.loc[ii]['Тип объекта'])
    s = re.findall('площадью .{1,} кв.м.', df.loc[ii]['Описание'])
    if len(s) > 0:
        sqs.append(float(s[0].replace('площадью ', '').replace(' кв.м.', '')))
    else: sqs.append(df.loc[ii]['Общая площадь'])
    ii += 1

df['Тип объекта'] = types
df['Общая площадь'] = sqs   
    
df['Категория'] = [cat_dict[x][0] for x in list(df['Тип объекта'])]    
df['Подкатегория'] = [cat_dict[y][1] for y in list(df['Тип объекта'])]
df['Функционал'] = [cat_dict[z][2] for z in list(df['Тип объекта'])]
df = df.rename(columns={'Тип объявления': 'Сегмент рынка', 'Общая площадь': 'Площадь'})
df['Тип объявления'] = ['Аренда' for a in list(df['Тип объекта'])]
df['Ед. изм.'] = ['м²' for x in list(df['Тип объекта'])]


df = df.rename(columns={'Цена за м²': 'Цена за 1 ед. изм.', 'гео позиция': 'Координаты'})
#df = df.drop(['Этажей в здании', 'Широта', 'Долгота', 'цена за м²', 'п. Усть-Ордынский (центр)'], axis=1)
df = df.drop(['Широта', 'Долгота'], axis=1)
df = df[df['Координаты'] != '-']


#making regional datasets
for region in list(df['Регион'].unique()):
    df[df['Регион'] == region].to_excel(f'C:/Users/p.ignatenok/Documents/veranda/move/regions_rent_jan/move_rent_jan_2023_{region}_ext.xlsx')

