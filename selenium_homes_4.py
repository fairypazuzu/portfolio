#импорт модулей
from selenium import webdriver
import re
import pandas as pd

#добавляем справочник муниципалитетов
settlements = pd.read_excel('settlements.xlsx')

#запуск браузера
driver = webdriver.Firefox()

#указываем, что будем искать (загородные дома на продажу в Ленобласти)
query = {
    'deal_type': 'sale',
    'offer_type': 'suburban',
    'object_type': 1,
    'region': '4588'
}

#"детали" для ссылки
deal_type = 'deal_type=' + query['deal_type']
offer_type = 'offer_type=' + query['offer_type']
object_type = 'object_type[0]=' + str(query['object_type'])
region = 'region=' + query['region']  


#для ссылки: типы домов
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

#для ссылки: типы отопления
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

#для ссылки: типы санузлов
wc_site_types = {
    '1': 'В доме',
    '2': 'На улице'
    }

#список домов
listings = []

#для определения района
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

#список адресов
addresses = []

#прокручиваем все комбинации
for house_material in house_materials:
    for heating_type in heating_types:
        for electricity in [0, 1]:
            for gas in [0, 1]:
                for water in [0, 1]:
                    for drainage in [0, 1]:
                        for floors in [1, 2, 3]:
                            for wc_site_type in wc_site_types:
                                try:
                                    #создаем ссылку
                                    electricity_str = 'electricity=' + str(electricity)
                                    gas_str = 'gas=' + str(gas)
                                    water_str = 'water=' + str(water)
                                    drainage_str = 'drainage=' + str(drainage)
                                    floors_str = f'maxfloorn={floors}&minfloorn={floors}'
                                    material = 'house_material[0]=' + house_material
                                    heating = 'heating_type[0]=' + heating_type
                                    wc_site = 'wc_site=' + wc_site_type
                                    link = 'https://spb.cian.ru/cat.php?' + '&' + deal_type + '&' + material + '&' + heating + '&' + wc_site + '&' + floors_str + '&' + object_type + '&' + offer_type + '&' + electricity_str + '&' + gas_str + '&' + water_str + '&' + drainage_str + '&' + region
                                    driver.get(link)
                                    #считаем количество страниц по запросу
                                    flats = int(driver.find_element_by_tag_name('h5').text.replace('Найдено', '').replace('объявлений', '').replace('объявления', '').replace('объявление', '').replace(' ', ''))
                                    if (flats % 28) == 0:
                                        total_pages = (flats/28)
                                    else: total_pages = ((flats/28)+1)
                                    page = 1
                                    #листаем страницы
                                    while page<total_pages:
                                        p = 'page=' + str(page)
                                        url = 'https://spb.cian.ru/cat.php?' + '&' + deal_type + '&' + material + '&' + heating + '&' + wc_site + '&' + floors_str + '&' + object_type + '&' + offer_type + '&' + electricity_str + '&' + gas_str + '&' + water_str + '&' + drainage_str + '&' + p + '&' + region
                                        driver.get(url)
                                        page_text = driver.find_element_by_tag_name('html').text.split('Дополнительные предложения по вашему запросу')[0]
                                        group = '\n.{1,}'
                                        #различные объявления содержат различное количество "ненужных" строк между своими частями, учитываем это
                                        for x in [0, 1, 2]:
                                            for y in [0, 1, 2]:
                                                #создаем регулярные выражения
                                                pattern1 = '\nДом, .{1,} м², .{1,}' + group*x + '\n.{1,} шоссе\n.{1,} км от КАД' + group*y + '\nЛенинградская область, .{1,}\n.{1,} ₽' + group*4
                                                pattern2 = '\nКоттедж, .{1,} м², .{1,}' + group*x + '\n.{1,} шоссе\n.{1,} км от КАД' + group*y + '\nЛенинградская область, .{1,}\n.{1,} ₽' + group*4
                                                res = re.findall(f'{pattern1}|{pattern2}', page_text)
                                                #просматриваем все результаты, определяем значения параметров дома/коттеджа
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
                                                    if len(rx[0].split(', '))>3:
                                                        listing['form'] = rx[0].split(', ')[3].replace(' ', '')
                                                    else: listing['form'] = 'не определен'
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
                                                    elif ('Сосновый Бор' in rx[3+x+y].split(', ')[2]):
                                                         lty = rx[3+x+y].split(', ')[2]
                                                         listing['locality'] = rx[3+x+y].split(', ')[2]
                                                         listing['settlement'] = 'Сосновый Бор'
                                                         listings['district'] = 'Сосновоборский городской округ'
                                                    if 'district' not in listing:
                                                        listing['district'] = 'Ленинградская область'
                                                        listing['settlement'] = 'Ленинградская область'
                                                        listing['locality'] = 'Ленинградская область'
                                                    listing['price'] = float(rx[4+x+y].replace(' ', '').replace('₽', ''))
                                                    if rx[5+x+y].startswith('КП «'):
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
                                                    listing['electricity'] = electricity
                                                    listing['gas'] = gas
                                                    listing['water'] = water
                                                    listing['drainage'] = drainage
                                                    listing['floors'] = floors
                                                    #всю собранную информацию добавляем в общий список
                                                    listings.append(listing)
                                        page += 1
                                        print(len(listings))
                                except Exception as e: (f'{e}')

#создаем словарь для датафрейма 
listings_dict = {
    'type': [],
    'meters': [],
    'land': [],
    'form': [],
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
    'electricity': [],
    'gas': [],
    'water': [],
    'drainage': [],
    'floors': []
    } 

#преобразуем список домов в словарь
for listing_dict in listings:
    for key in listing_dict:
        listings_dict[key].append(listing_dict[key])
        

#создаем датафрейм
df = pd.DataFrame(listings_dict).drop_duplicates() 
df['price_per_meter'] = df['price']/df['meters']
df['commodities'] = df['electricity'] + df['gas'] + df['water'] + df['drainage']   

print(df)    

#создаем эксель
df.to_excel('selenium_homes_4_4.xlsx', sheet_name='homes')
