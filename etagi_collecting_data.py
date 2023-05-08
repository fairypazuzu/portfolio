#importing modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import textwrap
#import pymongo
import pandas as pd
#import nextcloud_client
import os

#setting options for chromedriver
options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

#downloading links
docs_list = pd.read_excel('etagi_sell_links_may_clear.xlsx').drop('Unnamed: 0', axis=1)
docs_list = docs_list.rename(columns={'ID': 'links', 'Регион': 'regions'})


listings = []
errors_links = []
errors_regs = []

#docs_list = pd.read_excel('etagi_err_2.xlsx')

#launching this cycle
i = 0
while i < len(docs_list):

  try:
    listing_dict = {}
    driver.get(f'https://etagi.com/commerce/{docs_list.loc[i]["links"]}')
    #making a screenshot
    total_width = 1280
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(total_width, total_height)
    driver.save_screenshot('page_image.png')
    im = Image.open('page_image.png')
    #for a header
    img = Image.new('RGB', (im.size[0], 120), color = (132, 207, 255))
    fnt = ImageFont.truetype('Roboto-Black.ttf', 18)
    d = ImageDraw.Draw(img)
    lines = textwrap.wrap(f'ССЫЛКА: https://etagi.com/commerce/{docs_list.loc[i]["links"]}', width=70)
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
        merged_image.save(f'Z:/etagi_screenshots/{str(docs_list.loc[i]["links"])[:3]}/{docs_list.loc[i]["links"]}.jpg')
    except:
        os.mkdir(f'Z:/etagi_screenshots/{str(docs_list.loc[i]["links"])[:3]}')
        merged_image.save(f'Z:/etagi_screenshots/{str(docs_list.loc[i]["links"])[:3]}/{docs_list.loc[i]["links"]}.jpg')
    #getting raw data
    page_source = driver.page_source
    data = re.findall('var data=.{1,}</script><noscript><iframe', page_source)
    result = eval(data[0].replace('var data=', '').replace('</script><noscript><iframe', '').replace('false', ' False').replace('true', ' True').replace('null', ' None'))
    obj = result['objects']['commerceObject']
    listing_dict['Заголовок'] = driver.find_element(By.XPATH, '//span[@displayname="objectTitle"]').text
    listing_dict['Функционал'] = listing_dict['Заголовок'].split(', ')[0]
    listing_dict['Текст'] = obj['notes']
    listing_dict['Период аренды'] = obj['period']
    listing_dict['Широта'] = obj['la']
    listing_dict['Долгота'] = obj['lo']
    listing_dict['Координаты'] = f'{listing_dict["Широта"]} {listing_dict["Долгота"]}'
    listing_dict['Адрес'] = f'{obj["meta"]["city"]}, {obj["meta"]["street"]}, {obj["house_num"]}'
    listing_dict['Линия'] = obj['line']
    listing_dict['Категория'] = obj['class']
    listing_dict['Сегмент рынка'] = 'Продажа'
    listing_dict['Этаж'] = obj['floor']
    listing_dict['Этажность'] = obj['floors']
    listing_dict['Цена'] = obj['price']
    listing_dict['Площадь'] = obj['square']
    listing_dict['Цена за 1 ед. изм.'] = obj['price_m2']
    listing_dict['Паркинг'] = obj['parking']
    listing_dict['Год постройки'] = obj['building_year']
    listing_dict['Тип объекта'] = obj['type']
    listing_dict['Планировка'] = obj['planirovka']
    listing_dict['Опубликовано'] = obj['date_create'].split('T')[0]
    listing_dict['Обновлено'] = obj['date_update'].split('T')[0]
    listing_dict['Водоснабжение'] = obj['water_sources']
    listing_dict['Удобства'] = obj['has']
    if 'vent' in obj['additional_meta'].keys():
        listing_dict['Вытяжка'] = obj['additional_meta']['vent']
    else: listing_dict['Вытяжка'] = '-'
    if 'ceiling' in obj['additional_meta'].keys():
        listing_dict['Потолок'] = obj['additional_meta']['ceiling']
    else: listing_dict['Потолок'] = '-'
    if 'walls' in obj['additional_meta'].keys():
        listing_dict['Стены'] = obj['additional_meta']['walls']
    else: listing_dict['Стены'] = '-'
    if 'floor' in obj['additional_meta'].keys():
        listing_dict['Пол'] = obj['additional_meta']['floor']
    else: listing_dict['Пол'] = '-'
    if 'power' in obj['additional_meta'].keys():
        listing_dict['Мощность электричества'] = obj['additional_meta']['power']
    else: listing_dict['Мощность электричества'] = '-'
    if 'ceiling_height' in obj['additional_meta'].keys():
        listing_dict['Высота потолков'] = obj['additional_meta']['ceiling_height']
    else: listing_dict['Высота потолков'] = '-'
    listing_dict['Онлайн-показ'] = obj['online_showing']
    listing_dict['Количество входов'] = obj['entrance_cnt']
    listing_dict['Регион'] = docs_list.loc[i]["regions"]
    elements = driver.find_elements(By.XPATH, '//button[@class="Yxb8x jJShB dnGM3 _0LC_o GmYmq zPhuj"]')
    elements[0].click()
    photos = driver.find_elements(By.XPATH, '//img[@data-display-name="mobile-obj-img"]')
    listing_dict['Ссылки на фото'] = str([photo.get_attribute('src') for photo in photos])[1:-1]
    listing_dict['ID'] = docs_list.loc[i]["links"]
    if 'realtor' in result['objects'].keys():
        realtor = result['objects']['realtor']
        listing_dict['Агент'] = realtor['fio_original']
        listing_dict['Телефон агента'] = realtor['phone_original']
        listing_dict['Почта агента'] = realtor['email']
    else:
        listing_dict['Агент'] = '-'
        listing_dict['Телефон агента'] = '-'
        listing_dict['Почта агента'] = '-'
    listing_dict['Ссылка на скриншот'] = f'Z:/etagi_screenshots/{str(docs_list.loc[i]["links"])[:3]}/{docs_list.loc[i]["links"]}.jpg'
    listings.append(listing_dict)
    #saving data
    with open(f'D:/etagi_sell_may_2023_data/{listing_dict["ID"]}.txt', 'w', encoding='utf-8') as f:
        f.write(str(listing_dict))
        f.close()
  #saving errors  
  except Exception as err:
      print(err)
      with open(f'D:/etagi_sell_may_2023_errors/{docs_list.loc[i]["links"]}.txt', 'w', encoding='utf-8') as f:
          f.write(str(tuple(docs_list.loc[i])))
          f.close()
      errors_links.append(docs_list.loc[i]["links"])
      errors_regs.append(docs_list.loc[i]["regions"])
  print(i)
  i += 1
      
      
driver.quit()
errs = pd.DataFrame()

errs['links'] = errors_links
errs['regions'] = errors_regs

errs.to_excel('etagi_rent_jan_2023_err_1bis.xlsx')
