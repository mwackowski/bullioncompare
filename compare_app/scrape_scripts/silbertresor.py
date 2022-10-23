from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
from sqlalchemy import types, create_engine, sql
import json
import math
import sqlite3
from db_path import DB_PATH

nbpUrl = 'http://api.nbp.pl/api/exchangerates/rates/a/eur/'
jsonString = json.loads((requests.get(nbpUrl)).text)
currency = jsonString['code']
rateDate=jsonString['rates'][0]['effectiveDate']
rateVal=jsonString['rates'][0]['mid']


page_count=[]
page_urls_silver = [
#         ['1/10 oz',[0.1, '']],
#         ['1/4 oz', [0.25,'']],
        ['1/2 oz', [0.5, 'https://www.silbertresor.de/index.php?cat=c31_Silbermuenzen-1-2-Oz.html']],
    ['1 oz', [1, 'https://www.silbertresor.de/index.php?cat=c32_Silbermuenzen-1-Oz.html']],
    ['2 oz', [2, 'https://www.silbertresor.de/index.php?cat=c33_Silbermuenzen-2-Oz.html']],
    ['5 oz', [5, 'https://www.silbertresor.de/index.php?cat=c34_Silbermuenzen-5-Oz.html']],
    ['10 oz', [10, 'https://www.silbertresor.de/index.php?cat=c35_Silbermuenzen-10-Oz.html']],
    ['0,5 kg', [500/31.1034768, 'https://www.silbertresor.de/index.php?cat=c39_Silbermuenzen-1-2-KG.html']],
    ['1 kg', [1000/31.1034768, 'https://www.silbertresor.de/index.php?cat=c36_Silbermuenzen-1-KG.html']],
    ['10 kg', [10000/31.1034768, 'https://www.silbertresor.de/index.php?cat=c62_Silbermuenzen-10-KG.html']],
    ['other',[0, 'https://www.silbertresor.de/index.php?cat=c63_Kleine-Silbermuenzen.html']],
    
]
for x in range(len(page_urls_silver)):

    page = page_urls_silver[x][1][1]
    r = requests.get(page)
    soup = bs(r.text, 'html.parser')
    try:
        footer = soup.find('td', class_='smallText')
        footer_text = footer.text.split(' ')
        starting_article=int(footer_text[1])
        ending_article=int(footer_text[3])
        total_articles = int(footer_text[6])
        total_pages=math.ceil(total_articles/ending_article)
        for page_no in range(2, total_pages+1):
            page_urls_silver.append([page_urls_silver[x][0], [page_urls_silver[x][1][0], page + '&page=' + str(page_no)]])
    except AttributeError as e:
        print(f'{page} - {e}')

page_count=[]
page_urls_gold = [
#         ['1/10 oz',[0.1, '']],
#         ['1/4 oz', [0.25,'']],
    ['1/20 oz', [0.05, 'https://www.silbertresor.de/index.php?cat=c42_Goldmuenzen-1-20-Oz.html']],
    ['1/10 oz', [0.1, 'https://www.silbertresor.de/index.php?cat=c41_Goldmuenzen-1-10-Oz.html']],
    ['1/4 oz', [0.25, 'https://www.silbertresor.de/index.php?cat=c44_Goldmuenzen-1-4-Oz.html']],
    ['1/2 oz', [0.5, 'https://www.silbertresor.de/index.php?cat=c43_Goldmuenzen-1-2-Oz.html']],
    ['1 oz', [1, 'https://www.silbertresor.de/index.php?cat=c45_Goldmuenzen-1-Oz.html']],
    ['2 oz', [2, 'https://www.silbertresor.de/index.php?cat=c59_Goldmuenzen-2-Oz.html']],
    ['5 oz', [5, 'https://www.silbertresor.de/index.php?cat=c61_Goldmuenzen-5-Oz.html']],
    ['10 oz', [10, 'https://www.silbertresor.de/index.php?cat=c60_Goldmuenzen-10-Oz.html']],
    ['inne', [0, 'https://www.silbertresor.de/index.php?cat=c68_Historisches-Gold.html']],
    ['inne', [0, 'https://www.silbertresor.de/index.php?cat=c185_Kleine-Goldmuenzen.html']]

]
for x in range(len(page_urls_gold)):
    page = page_urls_gold[x][1][1]

    r = requests.get(page)
    soup = bs(r.text, 'html.parser')
    try:
        footer = soup.find('td', class_='smallText')
        footer_text = footer.text.split(' ')
        starting_article=int(footer_text[1])
        ending_article=int(footer_text[3])
        total_articles = int(footer_text[6])
        total_pages=math.ceil(total_articles/ending_article)
        for page_no in range(2, total_pages+1):
#             print(page_no)
            page_urls_gold.append([page_urls_gold[x][0], [page_urls_gold[x][1][0], page + '&page=' + str(page_no)]])
    except AttributeError as e:
        print(f'{page} - {e}')


urls = {'silver':[],
       'gold': []}
urls['silver']=page_urls_silver
urls['gold']=page_urls_gold

def find_price(x):
#     start= x.lower().find('nur')
    return float(x.split()[0].replace('.','').replace(',','.'))

import time
weights, weight_nums, names, prices, availability, links, img_links, price_val, price_curr, metals= ([] for i in range(10))
for metal in ['silver', 'gold']:
    for x in range(len(urls[metal])):
        r = requests.get(urls[metal][x][1][1])
        soup = bs(r.text, 'html.parser')
        body = soup.find('td', {"style" : "background-color: #f1f1f1;"})

        counter = 0
        for a in body.find_all('a'):
            try:
                if(counter%4)==0:
                    try:
                        img_link = 'https://www.silbertresor.de/' + a.find('img')['src']
                        # print(img_link)
                    except Exception as e:
                        img_link = None
                elif(counter%4)==1 and img_link is not None:
                    link = a['href']
                    name = a.text
                    # print(link)
                    # print(name)
                    # print('-'*100)
                    weight = urls[metal][x][0]
                    weight_num = float(urls[metal][x][1][0])
                    if metal == 'silver':
                        metals.append('Silver')
                    else:
                        metals.append('Gold')
                    links.append(link)
                    img_links.append(img_link)
                    names.append(name)
                    weights.append(weight)
                    weight_nums.append(weight_num)
            except Exception as e:
                print(e)
            finally:
                counter+=1
        for y in body.find_all('span', {"style": "font-weight:bold; font-size:16px; color:#008000;"}):
            prices.append(y.text[y.text.lower().find('nur')+4:].strip())
    time.sleep(1)
for p in prices:
    price_val.append(find_price(p))


import datetime
data_dzis = datetime.datetime.now().strftime('%Y-%m-%d')
data_godzina = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

import locale
locale.setlocale(locale.LC_ALL, '')
locale._override_localeconv = {'mon_thousands_sep': '.'}

df=pd.DataFrame()
df['WEIGHT']=weights
df['OZ']=weight_nums
df['NAME']=names
df['PRICE_TEXT']=prices
df['PRICE']=price_val
df['PRICE']=df['PRICE'] *rateVal
df['PRICE_PER_OZ'] = (df['PRICE']/df['OZ']).round(2)
# df['PRICE_PER_OZ'] = df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df['CURRENCY']='€'
df['AVAILABILITY']='available'
df['LINK']=links
df['SHOP']='Silbertresor'
df['IMG_LINK']=img_links
df['METAL']=metals
df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ'].astype(float)
df['PRICE_PER_OZ']= df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].round(2).apply(lambda x: '%.2f' % x).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.',','))
# df['PRICE_PER_OZ_PLN'] = (df['PRICE']/df['OZ']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł').apply(lambda x: x.replace('.',','))
# df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].apply(lambda x: locale.format_string('%.2f', x, grouping=True, monetary=True)).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.', ' '))
df['PRICE_PLN']= df['PRICE'].round(2).apply(lambda x: '%.2f' % x).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.', ','))
df['LOAD_TIME'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')



data_dzis = datetime.datetime.now().strftime('%Y-%m-%d')
data_godzina = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df['LOAD_TIME'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

df.drop(df[df.PRICE==0].index, inplace=True)

dtype = {c:types.VARCHAR(df[c].str.len().max())
        for c in df.columns[df.dtypes == 'object'].tolist()}


path = DB_PATH
conn = sqlite3.connect(path)
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
    'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings_all', conn, if_exists='append', index=False,  chunksize=1000)

cur = conn.cursor()

cur.execute("DELETE from compare_app_pricings where SHOP = 'Silbertresor'")
conn.commit()
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
  'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings', conn, if_exists='append', index=False, chunksize=1000)

try:
    conn.close()
except Exception as e:
    print(e)