from selenium import webdriver
import re
import pandas as pd


driver = webdriver.Firefox()

settlements = pd.read_excel('settlements.xlsx')

query = {
    'deal_type': 'rent',
    'offer_type': 'suburban',
    'type': 2, #2 - посуточно, 4 - продолжительно
    'object_type': 1,
    'region': '4588'
}

deal_type = 'deal_type=' + query['deal_type']
offer_type = 'offer_type=' + query['offer_type']
object_type = 'object_type[0]=' + str(query['object_type'])
region = 'region=' + query['region']  
rent_type = 'type=' + str(query['type'])

house_materials = {
    '1': 'Кирпичный',    
    '2': 'Монолитный',
    #'3': 'Панельный',
    #'4': 'Блочный',
    '5': 'Деревянный',
    #'6': 'Сталинский',
    '7': 'Щитовой',
    #'8': 'Кирпично-монолитный',
    '10': 'Каркасный',
    '11': 'Газобетонный блок',
    '12': 'Газосиликатный блок',
    '13': 'Пенобетонный блок'
    }

heating_types = {
    '1': 'Без отопления',
    '2': 'Центральное газовое',
    '3': 'Угольное',
    '4': 'Печь',
    '5': 'Камин',
    '6': 'Электрическое',
    '6300': 'Автономное газовое',
    '6301': 'Дизельное',
    '6302': 'Твердотопливный котел'
    }

wc_site_types = {
    '1': 'В доме',
    '2': 'На улице'
    }

repair_types = {
    '1': 'Без ремонта',
    '2': 'Косметический',
    '3': 'Евроремонт',
    '4': 'Дизайнерский'
    }


listings = []

districts_data = {
    'Бокситорогск': 'Бокситогорский',
    'Волосово': 'Волосовский',
    'Волхов': 'Волховский',
    'Всеволожск': 'Всеволожский',
    'Выборг': 'Выборгский',
    'Гатчина': 'Гатчинский',
    'Кингисепп': 'Кингисеппский',
    'Кириши': 'Киришский',
    'Кировск': 'Кировский',
    'Лодейное поле': 'Лодейнопольский',
    'Ломоносов': 'Ломоносовский',
    'Луга': 'Лужский',
    'Подпорожье': 'Подпорожский',
    'Приозерск': 'Приозерский',
    'Сланцы': 'Сланцевский',
    'Тихвин': 'Тихвинский',
    'Тосно': 'Тосненский'
    }


for house_material in house_materials:
    for heating_type in heating_types:
        for year in list(range(2000, 2022)):
                        for wc_site_type in wc_site_types:
                            for repair_type in repair_types:
                                try:
                                    print(len(listings))
                                    material = 'house_material[0]=' + house_material
                                    heating = 'heating_type[0]=' + heating_type
                                    wc_site = 'wc_site=' + wc_site_type
                                    repair = 'repair[0]=' + repair_type
                                    year_str = f'max_house_year={year}&min_house_year={year}'
                                    link = f'https://spb.cian.ru/cat.php?&{deal_type}&{material}&{heating}&{wc_site}&{rent_type}&{repair}&{object_type}&{offer_type}&{year_str}&{region}'
                                    driver.get(link)
                                    flats = int(driver.find_element_by_tag_name('h5').text.replace('Найдено', '').replace('объявлений', '').replace('объявления', '').replace('объявление', '').replace(' ', ''))
                                    if (flats % 28) == 0:
                                        total_pages = (flats/28)
                                    else: total_pages = ((flats/28)+1)
                                    page = 1
                                    while page<total_pages:
                                        p = 'page=' + str(page)
                                        url = f'https://spb.cian.ru/cat.php?&{deal_type}&{material}&{heating}&{wc_site}&{rent_type}&{repair}&{object_type}&{offer_type}&{year_str}&{p}&{region}'
                                        driver.get(url)
                                        page_text = driver.find_element_by_tag_name('html').text.split('Дополнительные предложения по вашему запросу')[0]
                                        group = '\n.{1,}'
                                        for x in [0, 1, 2]:
                                            for y in [0, 1, 2, 3, 4]:
                                                pattern1 = '\nДом, .{1,} м², .{1,}' + group*x + '\n.{1,} шоссе\n.{1,} км от КАД' + group*y + '\nЛенинградская область, .{1,}\n.{1,} ₽/сутки' + group*4
                                                pattern2 = '\nКоттедж, .{1,} м², .{1,}' + group*x + '\n.{1,} шоссе\n.{1,} км от КАД' + group*y + '\nЛенинградская область, .{1,}\n.{1,} ₽/сутки.' + group*4
                                                res = re.findall(f'{pattern1}|{pattern2}', page_text)
                                                for r in res:
                                                    listing = {}
                                                    if 'Получи ипотеку онлайн' in r:
                                                        rx = r[1:].split('\n').remove('Получи ипотеку онлайн')
                                                    rx = r[1:].split('\n')
                                                    listing['type'] = rx[0].split(', ')[0]
                                                    listing['meters'] = float(rx[0].split(', ')[1].replace('м²', '').replace(' ', '').replace(',', '.'))
                                                    if 'сот.' in rx[0].split(', ')[2]:
                                                        listing['land'] = float(rx[0].split(', ')[2].replace('сот.', '').replace(' ', ''))
                                                    elif 'га' in rx[0].split(', ')[2]:
                                                        listing['land'] = float(rx[0].split(', ')[2].replace('га', '').replace(' ', ''))*100
                                                    listing['floors'] = float(rx[0].split(', ')[3].replace(' ', '').replace('этажа', '').replace('этаж', ''))
                                                    if len(rx[0].split(', '))>4:
                                                        listing['bedrooms'] = float(rx[0].split(', ')[4].replace(' ', '').replace('спальня', '').replace('спальни', '').replace('спален', ''))
                                                    else: listing['bedrooms'] = 'не определено'
                                                    listing['road'] = rx[1+x].replace(' шоссе', '')
                                                    listing['distance'] = float(rx[2+x].replace(' км от КАД', ''))
                                                    if 'район' in rx[3+x+y].split(', ')[1]:
                                                        listing['district'] = rx[3+x+y].split(', ')[1].replace(' район', '')
                                                        dst = listing['district'] + ' район'
                                                        if ('с/пос' in rx[3+x+y].split(', ')[2]):
                                                            listing['settlement'] = rx[3+x+y].split(', ')[2].replace('с/пос', 'сельское поселение')
                                                            listing['locality'] = rx[3+x+y].split(', ')[3]
                                                        elif ('городское поселение' in rx[3+x+y].split(', ')[2]):
                                                            listing['settlement'] = rx[3+x+y].split(', ')[2]
                                                            listing['locality'] = rx[3+x+y].split(', ')[3]
                                                        elif (('пгт' in rx[3+x+y].split(', ')[2]) and ('городское поселение' not in rx[3+x+y].split(', ')[2])):
                                                            lty = rx[3+x+y].split(', ')[2]
                                                            listing['locality'] = rx[3+x+y].split(', ')[2]
                                                            listing['settlement'] = list(settlements.query(f'район == "{dst}" and название == "{lty}"')['поселение'])[0]
                                                        else: 
                                                            lty = rx[3+x+y].split(', ')[2]
                                                            listing['locality'] = rx[3+x+y].split(', ')[2]
                                                            listing['settlement'] = list(settlements.query(f'район == "{dst}" and название == "{lty}"')['поселение'])[0]
                                                    elif 'район' in rx[3+x+y].split(', ')[2]:
                                                        listing['district'] = rx[3+x+y].split(', ')[2].replace(' район', '')
                                                        dst = listing['district'] + ' район'
                                                        if ('с/пос' in rx[3+x+y].split(', ')[3]):
                                                            listing['settlement'] = rx[3+x+y].split(', ')[3].replace('с/пос', 'сельское поселение')
                                                            listing['locality'] = rx[3+x+y].split(', ')[4]
                                                        elif ('городское поселение' in rx[3+x+y].split(', ')[3]):
                                                            listing['settlement'] = rx[3+x+y].split(', ')[3]
                                                            listing['locality'] = rx[3+x+y].split(', ')[4]
                                                        elif (('пгт' in rx[3+x+y].split(', ')[3]) and ('городское поселение' not in rx[3+x+y].split(', ')[3])):
                                                            lty = rx[3+x+y].split(', ')[3]
                                                            listing['locality'] = rx[3+x+y].split(', ')[3]
                                                            listing['settlement'] = list(settlements.query(f'район == "{dst}" and название == "{lty}"')['поселение'])[0]
                                                        else: 
                                                            lty = rx[3+x+y].split(', ')[3]
                                                            listing['locality'] = rx[3+x+y].split(', ')[3]
                                                            listing['settlement'] = list(settlements.query(f'район == "{dst}" and название == "{lty}"')['поселение'])[0]
                                                    
                                                    elif ('Сосновый Бор' in rx[3+x+y].split(', ')[2]):
                                                         lty = rx[3+x+y].split(', ')[2]
                                                         listing['locality'] = rx[3+x+y].split(', ')[2]
                                                         listing['settlement'] = 'Сосновый Бор'
                                                         listings['district'] = 'Сосновоборский городской округ'
                                                    if 'district' not in listing:
                                                        listing['district'] = 'Ленинградская область'
                                                        listing['settlement'] = 'Ленинградская область'
                                                        listing['locality'] = 'Ленинградская область'
                                                    listing['price'] = float(rx[4+x+y].replace(' ', '').replace('₽', '').replace('/сутки', '').replace('/мес.', ''))
                                                    """
                                                    if rx[5+x+y].startswith('На несколько месяцев'):
                                                        listing['status'] = 'На несколько месяцев'
                                                        listing['description'] = rx[5+x+y+1]
                                                        listing['actor'] = rx[6+x+y+1]
                                                        listing['agent'] = rx[7+x+y+1]                                                    
                                                    elif rx[5+x+y].startswith('От года'):
                                                        listing['status'] = 'От года'
                                                        listing['description'] = rx[5+x+y+1]
                                                        listing['actor'] = rx[6+x+y+1]
                                                        listing['agent'] = rx[7+x+y+1]   
                                                    else:
                                                        listing['status'] = 'не определено'
                                                        listing['description'] = rx[5+x+y]
                                                        listing['actor'] = rx[6+x+y]
                                                        listing['agent'] = rx[7+x+y]
                                                    """
                                                    if rx[5+x+y].startswith('Посуточно'):
                                                        listing['description'] = rx[5+x+y+1]
                                                        listing['actor'] = rx[6+x+y+1]
                                                        listing['agent'] = rx[7+x+y+1]  
                                                    else:
                                                        listing['description'] = rx[5+x+y]
                                                        listing['actor'] = rx[6+x+y]
                                                        listing['agent'] = rx[7+x+y]   
                                                    
                                                    listing['heating'] = heating_types[heating_type]
                                                    listing['material'] = house_materials[house_material]
                                                    listing['wc_site'] = wc_site_types[wc_site_type]
                                                    listing['repair'] = repair_types[repair_type]
                                                    listing['age'] = 2022-year
                                                    listings.append(listing)
                                        page += 1
                                except Exception as e: print(f'{e}')

listings_dict = {
    'type': [],
    'meters': [],
    'land': [],
    'road': [],
    'distance': [],
    'district': [],
    'settlement': [],
    'locality': [],
    'price': [],
    'description': [],
    'actor': [],
    'agent': [],
    'heating': [],
    'material': [],
    'wc_site': [],
    'repair': [],
    'floors': [],
    'bedrooms': [],
    'age': []
    } 

for listing_dict in listings:
    for key in listing_dict:
        listings_dict[key].append(listing_dict[key])
        

df = pd.DataFrame(listings_dict).drop_duplicates() 
#df['price_per_meter'] = df['price']/df['meters']
#df['commodities'] = df['electricity'] + df['gas'] + df['water'] + df['drainage']   

print(df)  

df.to_excel('selenium_rental_homes_1_6.xlsx', sheet_name='homes')  