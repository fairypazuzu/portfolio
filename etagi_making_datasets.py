#importing modules
import pandas as pd

#importing raw data
df = pd.read_excel('etagi_rent_2.xlsx')

#expanding columns
multi_cols = ['Удобства', 'Стены', 'Пол']

trad_cols = ['Линия', 'Категория', 'Тип объекта', 'Планировка', 'Водоснабжение', 'Вытяжка', 'Потолок']


ms = {}
for m in multi_cols:
    ms[m] = []
    for x in list(df[m]):
        if type(x) == str and x != '-':
            for y in eval(x):
                if y not in ms[m]:
                    ms[m].append(y)

    
for key in ms:
    for cat in ms[key]:
        ls = []
        for x in df[key]:
            if type(x) == str and x != '-':
                if cat in x:
                    ls.append('Да')
                else: ls.append('Нет')
            else: ls.append('Да')
        df[cat] = ls

items = pd.read_excel('items.xls')

item_dict = {}
for item in list(items['Колонка'].unique()):
    item_dict.update({item: {}})

i = 0
while i < len(items):
    item_dict[items.loc[i]['Колонка']][items.loc[i]['Объект']] = items.loc[i]['Значение']
    i += 1


for col in item_dict:
    new_col = []
    for x in list(df[col]):
        try:
            new_col.append(item_dict[col][x])
        except: new_col.append('-')
    df[col] = new_col
 
#changing values
df = df.rename(columns={
    'phone': 'Телефон',
    'internet': 'Интернет',
    'conditioner': 'Кондиционер',
    'air_filters': 'Воздушный фильтр',
    'fire_signal': 'Пожарная сигнализация',
    'safe_signal': 'Сигнализация',
    'ohrana': 'Охрана',
    'water_filters': 'Водяные фильтры',
    'okraska': 'Окраска стен',
    'shtukaturka': 'Штукатурка',
    'oboi': 'Обои',
    'styazhka': 'Стяжка',
    'plitka': 'Плитка',
    'komlin': 'Коммерческий линолеум',
    'nalivnoy': 'Наливной пол',
    'parket': 'Паркет'
    })

df = df.drop(['Unnamed: 0', 'regs_app'], axis=1)

park = []
for x in df['Паркинг']:
    if x:
        park.append('Да')
    else: park.append('Нет')
    
df['Паркинг'] = park

show = []
for x in df['Онлайн-показ']:
    if x:
        show.append('Да')
    else: show.append('Нет')
    
df['Онлайн-показ'] = show

categories = pd.read_excel('cats.xlsx')

cat_dict = {}
i = 0
while i < len(categories):
    cat_dict.update({categories.loc[i]['list']: [categories.loc[i]['cat'], categories.loc[i]['sub']]})
    i += 1
#assigning categories   
df['Категория'] = [cat_dict[x][0] for x in list(df['Тип объекта'])]    
df['Подкатегория'] = [cat_dict[x][1] for x in list(df['Тип объекта'])]
df = df.rename(columns={'Тип объявления': 'Сегмент рынка', 'Онлайн-показ': 'Online-показ', 'Паркинг': 'Парковка'})
df['Тип объявления'] = ['Аренда' for x in list(df['Тип объекта'])]
df['Ед. изм.'] = ['м²' for x in list(df['Тип объекта'])]

df = df.drop(['Широта', 'Долгота', 'Удобства', 'Пол', 'Стены', 'Сегмент рынка'], axis=1)

df = df.query('Координаты != "None None"')

#clearing data
for column in list(df.columns):
    new_column = []
    for x in list(df[column]):
        if str(x) != 'nan':
            new_column.append(x)
        else: new_column.append('-')
    df[column] = new_column

#making regional datasets            
for region in list(df['Регион'].unique()):
    df[df['Регион']==region].to_excel(f'./regions_rent_ext/etagi_rent_{region}_ext.xlsx')