from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from sqlalchemy import types, sql
import re
import numpy as np
import json
import datetime

import sqlite3
from db_path import DB_PATH

europeanMintUrls = ['https://www.europeanmint.com/silver-bullion/', 'https://www.europeanmint.com/gold-bullion/']

nbpUrl = 'http://api.nbp.pl/api/exchangerates/rates/a/eur/'
jsonString = json.loads((requests.get(nbpUrl)).text)
currency = jsonString['code']
rateDate=jsonString['rates'][0]['effectiveDate']
rateVal=jsonString['rates'][0]['mid']


def find_weight(x):
    value = ['inne', 0,0]
    weights_dict = {'1/20': 0.05, '1/10': 0.1, '1/4': 0.25, '1/2': 0.5, '1': 1, '1.5': 1.5,
                    '2': 2, '30': 30/31.1034768, '5': 5, '10': 10,
                    '1 Kilo': 1000/31.1034768, '2 Kilo': 2000/31.1034768, '5 Kilo': 5000/31.1034768}

    rev_weight_dict = {
                    'oz': { 0.05: '1/20 oz', 0.1: '1/10 oz', 0.25: '1/4 oz', 0.5: '1/2 oz',
                   1: '1 oz', 2: '2 oz', 30/31.1034768: '30 g', 5: '5 oz', 10: '10 oz',
                  0: 0},
                   'gram' : { 0.05: '1/20 g', 0.1: '1/10 g', 0.25: '1/4 g', 0.5: '1/2 g',
                   1: '1 g', 2: '2 g', 30/31.1034768: '30 g', 5: '5 g', 10: '10 g'},
                  'inne': {0: 'inne'}
                  }

    found = False
    if re.search(r'\bgram\b', x, re.IGNORECASE) or re.search(r'\bgrams\b', x, re.IGNORECASE):
        weight_to_search = 'gram'
    else:
        weight_to_search = 'oz'
    if re.search(r'\bmonsterbox\b', x, re.IGNORECASE) or re.search(r'\bmonster box\b', x, re.IGNORECASE) or re.search(r'\bkilo\b', x, re.IGNORECASE) or re.search(r'\bducat\b', x, re.IGNORECASE):
        value = ('inne', 0)
    else:
        found = False
        for y in weights_dict:
            if not found:
                if re.search(rf'\b{y} {weight_to_search}\b', x, re.IGNORECASE) or re.search(rf'\b{y}g\b', x, re.IGNORECASE) or re.search(rf'\b{y}{weight_to_search}\b', x, re.IGNORECASE):
#                         print(x, y, weights_dict.get(y))
#                     value = (weight_to_search, weights_dict.get(y))
                    value = [rev_weight_dict[weight_to_search][weights_dict.get(y)], weights_dict.get(y), weight_to_search]
                    found = True
                else:
                    for z in x.split(' '):
                        if not found:
                            if z in weights_dict.keys():
#                                     print(x, z, weights_dict.get(z))
#                                 value = (weight_to_search, weights_dict.get(z))
                                value = [rev_weight_dict[weight_to_search][weights_dict.get(z)], weights_dict.get(z), weight_to_search]
                                found = True
                            else:
                                value = ['inne', 0,0]

    if value[2] == 'gram':
        ret_val = (value[0], value[1]/31.1034768)
    else:
        ret_val = (value[0], value[1])
    return ret_val


weights, weight_nums, names, prices, availability, links, img_links, price_val, price_curr, metals= ([] for i in range(10))
for x in range(len(europeanMintUrls)):
    r = requests.get(europeanMintUrls[x])
    soup = bs(r.text, "lxml")
    for c in ['item first col-xs-12 col-sm-4', 'item col-xs-12 col-sm-4', 'item last col-xs-12 col-sm-4']:
        for product in soup.find_all('li', class_=c):
            name = product.find('h2', class_='product-name')
            try:
                weight_tuple = find_weight(name.text)
            except Exception as e:
                print(e)
                weight_tuple= ('inne',0)
            weight_num = weight_tuple[1]
            weight = weight_tuple[0]


            link = name.a['href']
            img_link = product.img['src']
            price = product.find('div', class_='price-box').find('span', class_='price').text.strip()
            try:
                av = product.find('div', class_='actions').p.text.strip()
            except Exception as e:
                av = product.find('div', class_='actions').span.text.strip()
            names.append(name.text)
            weights.append(weight)
            weight_nums.append(weight_num)
            prices.append(price)
            links.append(link)
            img_links.append(img_link)
            availability.append(av)
            if x == 0:
                metals.append('Silver')
            else:
                metals.append('Gold')

            #print('{} {} {} {} {} {} {}'.format(name.text, price, weight, link, img_link, weight_tuple, av))


price_val = []
price_curr = []
for x in prices:
    price_curr.append(x[x.find('€')])
    price_val.append(x[x.find('€')+1:len(x)].replace(',',''))



df=pd.DataFrame()
df['WEIGHT']=weights
df['OZ']=weight_nums
df['NAME']=names
df['PRICE_TEXT']=prices
df['PRICE']=price_val
df['PRICE']=df['PRICE'].map(lambda x: x.replace(',','.')).astype(float) *rateVal
df['PRICE_PER_OZ'] = (df['PRICE']/df['OZ']).round(2)
df['PRICE_PER_OZ'] = df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df['CURRENCY']=price_curr
df['AVAILABILITY']=availability
df['LINK']=links
df['SHOP']='EuropeanMint'
df['IMG_LINK']=img_links
df['METAL']=metals
df['PRICE_PER_OZ_PLN'] = (df['PRICE']/df['OZ']).round(2)
df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].round(2).apply(lambda x: '%.2f' % x).replace('inf','-').astype(str).apply(lambda x: x+' zł' if x!='-' else x).apply(lambda x: x.replace('.',','))
df['PRICE_PLN']= (df['PRICE']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł' if x!='-' else x).apply(lambda x: x.replace('.',','))


data_dzis = datetime.datetime.now().strftime('%Y-%m-%d')
data_godzina = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df['LOAD_TIME'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


dtype = {c:types.VARCHAR(df[c].str.len().max())
        for c in df.columns[df.dtypes == 'object'].tolist()}


path = DB_PATH
conn = sqlite3.connect(path)
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
    'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings_all', conn, if_exists='append', index=False,  chunksize=1000)

cur = conn.cursor()

cur.execute("DELETE from compare_app_pricings where SHOP = 'EuropeanMint'")
conn.commit()
df[df['AVAILABILITY'].apply(lambda x: x.strip())!='Out of stock']\
[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
  'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings', conn, if_exists='append', index=False, chunksize=1000)

try:
    conn.close()
except Exception as e:
    print(e)