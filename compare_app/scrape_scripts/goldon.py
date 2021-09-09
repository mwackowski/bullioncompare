from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
from sqlalchemy import types, sql
import json
import sqlite3



urls = {'silver':[],
       'gold': []}


page_urls_silver = [
        ['1 oz',[1, 'https://www.goldon.pl/srebro-inwestycyjne-a/masa-1-oz,dCw-FA.html']],
        ['2 oz', [2,'https://www.goldon.pl/srebro-inwestycyjne-a/masa-2-oz,dCw-HQ.html']],
        ['10 oz', [10, 'https://www.goldon.pl/srebro-inwestycyjne-a/masa-10-oz,dCw-Sg.html']],
        ['30 g', [30/31.1034768, 'https://www.goldon.pl/srebro-inwestycyjne-a/masa-30-g,dCw-Iw.html']],
        ['1 1/2 oz', [1.5, 'https://www.goldon.pl/srebro-inwestycyjne-a/masa-1-5-oz,dCw-KQ.html']],
        ['1/2 oz', [0.5, 'https://www.goldon.pl/srebro-inwestycyjne-a/masa-1-2-oz,dCw-GA.html']],
        ['1 kg', [1000/31.1034768, 'https://www.goldon.pl/srebro-inwestycyjne-a/masa-1-kg,dCw-SQ.html']]]

for x in range(len(page_urls_silver)):
    page = page_urls_silver[x][1][1]

    equal = True
    counter=1
    while equal:
        splitted = page.split('.')
        splitted = [y+'/'+str(counter)+',P' if splitted.index(y)==2 else y for y in splitted]
        link = ".".join(splitted)
        r = requests.get(link)
        soup = bs(r.text, "lxml")
        if soup.find('link', {"rel" : "canonical"})['href'] == link:
            counter+=1
            page_urls_silver.append([page_urls_silver[x][0], [page_urls_silver[x][1][0], link]])
#             print(counter)
        else:
            equal = False
#         print(link)
#         print(soup1.find('link', {"rel" : "canonical"})['href'])
    if counter==20:
        break


page_urls_gold = [
        ['1 oz',[1, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-1-oz,dCw-FA.html']],
        ['10 g', [10/31.1034768, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-10-g,dCw-Mg.html']],
        ['5 g', [5/31.1034768, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-5-g,dCw-lA.html']],
        ['1/10 oz', [0.1, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-1-10-oz,dCw-Hg.html']],
        ['100 g', [100/31.1034768, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-100-g,dCw-Lg.html']],
        ['50 g', [50/31.1034768, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-50-g,dCw-Kw.html']],
        ['1/2 oz', [0.5, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-1-2-oz,dCw-GA.html']],
        ['15,04 g', [15.04/31.1034768, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-15-04-g,dCw-ww.html']],
        ['6,1 g', [6.1/31.1034768, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-6-10-g,dCw-wg.html']],
        ['1/4 oz', [0.25, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-1-4-oz,dCw-HA.html']],
        ['3,44 g', [3.44/31.1034768, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-3-44-g,dCw-rw.html']],
        ['7,32 g', [7.32/31.1034768, 'https://www.goldon.pl/zloto-inwestycyjne-a/masa-7-32-g,dCw-Tw.html']]

]


for x in range(len(page_urls_gold)):
    page = page_urls_gold[x][1][1]
    equal = True
    counter=1
    while equal:
        splitted = page.split('.')
        splitted = [y+'/'+str(counter)+',P' if splitted.index(y)==2 else y for y in splitted]
        link = ".".join(splitted)
        r = requests.get(link)
        soup = bs(r.text, "lxml")
        if soup.find('link', {"rel" : "canonical"})['href'] == link:
            counter+=1
            page_urls_gold.append([page_urls_gold[x][0], [page_urls_gold[x][1][0], link]])
#             print(counter)
        else:
            equal = False
#         print(link)
#         print(soup.find('link', {"rel" : "canonical"})['href'])
    if counter==20:
        break

urls['silver']=page_urls_silver
urls['gold']=page_urls_gold

import time
weights, weight_nums, names, prices, availability, links, img_links, price_val, price_curr, metals= ([] for i in range(10))
for metal in ['silver', 'gold']:
    for x in range(len(urls[metal])):
        r = requests.get(urls[metal][x][1][1])
        soup = bs(r.text, "lxml")
        for product in soup.find_all('article', class_='tile product-tile grid-3'):
            links_section = product.find('div', class_='image')
            link = 'https://www.goldon.pl' + links_section.find('span')['data-href']
            img_link = 'https://www.goldon.pl' + links_section.find('img')['src']

            text_section = product.find('footer', class_='product-tile__footer')
            name = ' '.join(text_section.find('p').text.strip().split())
            price = float(product.find('span', class_='price-value')['content'])
            av = product.find('link', {"itemprop" : "availability"})['href'].split('/')[3]
            weight = urls[metal][x][0]
            weight_num = float(urls[metal][x][1][0])

            links.append(link)
            img_links.append(img_link)
            names.append(name)
            prices.append(price)
            availability.append(av)
            weights.append(weight)
            weight_nums.append(weight_num)
            if metal == 'silver':
                metals.append('Silver')
            else:
                metals.append('Gold')
            #print(name, price, link, weight, str(weight_num), img_link, av)
            #print('-'*50)


df=pd.DataFrame()
df['WEIGHT']=weights
df['OZ']=weight_nums
df['NAME']=names
df['PRICE_TEXT']=prices
df['PRICE']=prices
df['PRICE_PER_OZ'] = ((df['PRICE'])/df['OZ']).round(2)
df['CURRENCY']='zł'
df['AVAILABILITY']=availability
df['LINK']=links
df['SHOP']='Goldon'
df['IMG_LINK']=img_links
df['METAL']=metals
df['PRICE_PER_OZ_PLN'] = (df['PRICE']/df['OZ']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł').apply(lambda x: x.replace('.',','))
df['PRICE_PLN']= df['PRICE'].apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł').apply(lambda x: x.replace('.',','))

from db_path import DB_PATH
path = DB_PATH
# print (path)
import datetime
data_dzis = datetime.datetime.now().strftime('%Y-%m-%d')
data_godzina = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df['LOAD_TIME'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

dtype = {c:types.VARCHAR(df[c].str.len().max())
        for c in df.columns[df.dtypes == 'object'].tolist()}

conn = sqlite3.connect(path)
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
    'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings_all', conn, if_exists='append', index=False,  chunksize=1000)

cur = conn.cursor()
try:
    cur.execute("DELETE from compare_app_pricings where SHOP = 'Goldon'")
except sqlite3.OperationalError as e:
    print(e)
conn.commit()
df[df['AVAILABILITY'].apply(lambda x: x.strip())=='InStock']\
[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
  'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings', conn, if_exists='append', index=False, chunksize=1000)

try:
    conn.close()
except Exception as e:
    print(e)