from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from sqlalchemy import types, create_engine, sql
import re
import numpy as np
import json
import datetime
import math

import sqlite3
from db_path import DB_PATH

metalmarketurls= ['https://www.metalmarket.eu/sw/menu/monety/srebrne-monety-851.html', 
                  'https://www.metalmarket.eu/sw/menu/monety/zlote-monety-850.html']

metalmarketurspaged=[]
for x in range(len(metalmarketurls)):
    r = requests.get(metalmarketurls[x])
    soup = bs(r.text, 'lxml')
    
    total_pages = soup.find('span', class_="navigation_total").find('b').text

    pages = math.ceil(int(total_pages.strip())/30)

    for page in range(pages):
        if x == 0:
            metalmarketurspaged.append('https://www.metalmarket.eu/sw/menu/monety/srebrne-monety-851.html?counter=' + str(page))
        else:
            metalmarketurspaged.append('https://www.metalmarket.eu/sw/menu/monety/zlote-monety-850.html?counter=' + str(page))

def find_weight(x):

    weights_dict = {'1/25': 0.04, '1/20': 0.05, '1/10': 0.1, '1/4': 0.25, '1/2': 0.5, '1': 1, 
                    '2': 2, '5': 5, '10': 10, '20': 20, '30': 30, '100': 100, '50': 50}
    
    rev_weight_dict = {
                    'oz': { 0.04: '1/25 g', 0.05: '1/20 oz', 0.1: '1/10 oz', 0.25: '1/4 oz', 0.5: '1/2 oz', 
                   1: '1 oz', 2: '2 oz', 5: '5 oz', 10: '10 oz', 20: '20 oz', 50: '50 oz', 
                  0: 0},
        
                   'g' : { 0.04: '1/25 g', 0.05: '1/20 g', 0.1: '1/10 g', 0.25: '1/4 g', 0.5: '1/2 g', 
                   1: '1 g', 2: '2 g', 20: '20 g', 30: '30 g', 5: '5 g', 10: '10 g', 50: '50 g', 100: '100 g'},
        
                  'kg': {1: '1 kg', 2: '2 kg', 5: '5 kg', 10: '10 kg'},
                  'other': {0: 'other'}
                  }
    exclude_list = ['pakiet', 'zł', 'zestaw', '5 Euro', '10 Euro', '20 Euro', '100 Euro', '50 Euro']
    value = None
    found = False
    for excluded in exclude_list:
        if re.search(rf"\b{excluded}\b", x, re.IGNORECASE):
            value = (0, 'other')
            break;
        else:
            for a in weights_dict:
                if re.search(rf"\b{a}[ ]g\b", x, re.IGNORECASE) or re.search(rf"\b{a}[ ]gram\b", x, re.IGNORECASE) \
                    or re.search(rf"\b{a}[ ]gramów\b", x, re.IGNORECASE):
                    value = (weights_dict[a], 'g')
                elif re.search(rf"\b{a}[ ]kilo\b", x, re.IGNORECASE) or re.search(rf"\b{a}[ ]kg\b", x, re.IGNORECASE):
                    value = (weights_dict[a], 'kg')
                elif re.search(rf"\b{a}oz\b", x, re.IGNORECASE) or re.search(rf"\b{a} oz\b", x, re.IGNORECASE):
                    value = (weights_dict[a], 'oz')
                elif re.search(rf"\b{a} uncj\w+\b", x, re.IGNORECASE) or re.search(rf"\b{a}uncj\w+\b", x, re.IGNORECASE):
                    value = (weights_dict[a], 'oz')
                if value is not None:
                    break

    if value is None:
        for b in weights_dict:
            if found:
                break
            else:
                for c in x.split(' '):
                    if b == c:
                        value = (b, 'oz')
                        found = True
                        break
                    else:
                        value = (0, 'other')

    if value[1] == 'g':
        weight_in_oz = value[0]/31.1034768
    elif value[1] == 'kg':
        weight_in_oz = value[0]*1000/31.1034768
    elif value[1] == 'other':
        weight_in_oz = 0
    else:
        weight_in_oz = value[0]
    if value[1] == 'other':
        return_string = (value[1], str(weight_in_oz))
    else:
        return_string = (rev_weight_dict[value[1]][value[0]], str(weight_in_oz))
    return return_string

def find_price(price):
    price_val = price.replace('\xa0', ' ')
    price_val = (price_val[:price_val.find('zł')].strip().replace(' ','').replace(',','.')) 
    return price_val

# def find_img(link):
#     r = requests.get(link)
#     soup = bs(r.text)
#     print(soup.find('div', class_='photos col-md-6 col-xs-12').find('img', class_='photo')['src'])


weights, weight_nums, names, prices, availability, links, img_links, price_val, price_curr, metals= ([] for i in range(10))

for x in range(len(metalmarketurspaged)):
    r = requests.get(metalmarketurspaged[x])
    soup = bs(r.text, 'lxml')

    for product in soup.find_all('div', class_="product_wrapper"):
        try:
            link = 'https://metalmarket.eu' + product.find('a', class_='product-icon align_row')['href']
            name = product.find('a', class_='product-name').text
    #         name = name.replace('uncja', 'oz').replace('uncje', 'oz').replace('uncji', 'oz').replace('Uncji', 'oz').replace('Uncja', 'oz').replace('Uncje', 'oz')
            price = product.find('div', class_='product_prices').text.strip()
            img = '' #'https://metalmarket.eu' + product.find('img', class_='b-lazy')['src']
            if price.strip() == 'Cena na telefon':
                price_val.append('Cena na telefon')
                price_curr.append('')
            else:
                price_val.append(find_price(price))
                price_curr.append('zł')
            try:
                weight = find_weight(name)[0]
                weight_num = float(find_weight(name)[1])
                weights.append(weight)
                weight_nums.append(weight_num)
            except Exception as e:
                print(e)
                #print(name)
                weights.append('other')
                weight_nums.append(0)
            links.append(link)
            img_links.append(img)
            names.append(name)
            
            prices.append(price)
            
            if metalmarketurspaged[x].find('srebrne') > 0:
                metal = 'Silver'
            else: metal = 'Gold'
            metals.append(metal)
        except Exception as e:
            print(e)


df=pd.DataFrame()
df['WEIGHT']=weights
df['OZ']=weight_nums
df['NAME']=names
df['PRICE_TEXT']=prices
df['PRICE_TEXT'] = df['PRICE_TEXT'].apply(lambda x: x.replace(' ', ''))
df['PRICE']=price_val

df['CURRENCY']=price_curr
df['AVAILABILITY']='available'
df['LINK']=links
df['SHOP']='MetalMarket'
df['IMG_LINK']=img_links
df['METAL']=metals
df = df[df['PRICE']!='Cena na telefon']

df.loc[:,'PRICE'] = df['PRICE'].astype(np.float64)
df.loc[:,'PRICE_PER_OZ'] = (df['PRICE']/df['OZ']).round(2)
df.loc[:,'PRICE_PER_OZ'] = df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df.loc[:,'PRICE_PER_OZ_PLN'] = (df['PRICE']/df['OZ']).round(2)
df.loc[:,'PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].round(2).apply(lambda x: '%.2f' % x).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.',','))
df.loc[:,'PRICE_PLN']= (df['PRICE']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.',','))

data_dzis = datetime.datetime.now().strftime('%Y-%m-%d')
data_godzina = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df.loc[:,'LOAD_TIME'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

dtype = {c:types.VARCHAR(df[c].str.len().max())
        for c in df.columns[df.dtypes == 'object'].tolist()}
path = DB_PATH
conn = sqlite3.connect(path)
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
    'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings_all', conn, if_exists='append', index=False,  chunksize=1000)

cur = conn.cursor()

cur.execute("DELETE from compare_app_pricings where SHOP = 'MetalMarket'")
conn.commit()
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
  'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings', conn, if_exists='append', index=False, chunksize=1000)

try:
    conn.close()
except Exception as e:
    print(e)
 