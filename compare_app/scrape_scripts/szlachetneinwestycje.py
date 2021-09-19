from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from sqlalchemy import types, create_engine, sql
import re, json, datetime, lxml, math
import numpy as np

import sqlite3
from db_path import DB_PATH
import asyncio
import aiohttp

urls_base = {'Silver': ['https://sklep.szlachetneinwestycje.pl/srebro/'],
            'Gold': ['https://sklep.szlachetneinwestycje.pl/zloto/']}
srebro, zloto = [], []
urls_final = {}
for k, v in urls_base.items():
    for x in v:
        r = requests.get(x)
        soup = bs(r.text, 'lxml')
        paginator = soup.find('p', class_='woocommerce-result-count').text
        # print(x, paginator)
        if paginator.strip() == 'Wyświetlanie jednego wyniku' or paginator.find('wszystkich') != -1:
            page_no=1
        else:
            p_list = paginator.strip().split(' ')
            first=p_list[1][p_list[1].find('–')+1:]
            last = p_list[3]
            page_no = math.ceil(int(last)/int(first))
        for pages in range(1, page_no+1):
            if k == 'Silver':
                srebro.append(f'{x}page/{pages}/')
            else:
                zloto.append(f'{x}page/{pages}/')
urls_final['Silver']=srebro
urls_final['Gold']=zloto

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
    exclude_list = ['pakiet', 'zł', 'dukat']
    value = None
    found = False
    for excluded in exclude_list:
        if re.search(rf"\b{excluded}\b", x, re.IGNORECASE):
            value = (0, 'other')
            break
        else:
            for a in weights_dict:
                if re.search(rf"\b{a}[ ]g\b", x, re.IGNORECASE) or re.search(rf"\b{a}[ ]gram\b", x, re.IGNORECASE) \
                    or re.search(rf"\b{a}[ ]gramów\b", x, re.IGNORECASE):
                    value = (weights_dict[a], 'g')
                elif re.search(rf"\b{a}[ ]kilo\b", x, re.IGNORECASE) or re.search(rf"\b{a}[ ]kg\b", x, re.IGNORECASE):
                    value = (weights_dict[a], 'kg')
                elif re.search(rf"\b{a}[ ]uncj\w\b", name, re.IGNORECASE):
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
        return_string = (value[1], weight_in_oz)
    else:
        return_string = (rev_weight_dict[(value[1])][(value[0])], (weight_in_oz))
    return return_string


def find_price(price):
    price = price.replace('od', '')
    price_val = (price[:price.find('zł')].strip().replace(' ','').replace(',','.')) 
    return float(price_val)

async def main():
    async with  aiohttp.ClientSession() as session:    
        tasks = []      
        for metal, urls in urls_final.items():
            for x in urls:
                # print(x)
                task = asyncio.ensure_future(send_request(session, x, metal))
                tasks.append(task)
            results = await asyncio.gather(*tasks)                                  
        return results

async def send_request(session, url, metal):
    async with session.get(url, headers=header) as response:
        result_data = await response.read()
        return (result_data.decode(), metal)

header = {'Accept-Encoding': 'gzip', 'accept-language': '*'}

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
outcome = loop.run_until_complete(main())

try:
    loop.close()
except RuntimeError as e:
    print(e)

weights, weight_nums, names, prices, links, img_links, price_val, price_curr, metals= ([] for i in range(9))

for x in outcome:
    soup = bs(x[0], 'lxml')
    li = soup.find_all('li', class_='product')
    for l in li:
        try:
            img = l.find('img', class_='attachment-woocommerce_thumbnail')['data-lazy-src']
            name = l.find('h2', class_='woocommerce-loop-product__title').text
            price = l.find('span', class_='price').text

            href = l.find('a', class_='woocommerce-LoopProduct-link')['href']
            weights.append(find_weight(name)[0])
            weight_nums.append(find_weight(name)[1])
            names.append(name)
            prices.append(price)

            links.append(href)
            img_links.append(img)
            price_val.append(find_price(price))

            metals.append(x[1])
            # print(name.strip(), price.strip(), href, find_weight(name), metal, find_price(price))
        except Exception as e:
            print(e)

df=pd.DataFrame()
df['WEIGHT']=weights
df['OZ']=weight_nums
df['NAME']=names
df['PRICE_TEXT']=prices
df['PRICE_TEXT'] = df['PRICE_TEXT'].apply(lambda x: x.replace('\xa0zł', 'PLN'))
df['PRICE']=price_val
df['PRICE_PER_OZ'] = (df['PRICE']/df['OZ']).round(2)
df['PRICE_PER_OZ'] = df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df['CURRENCY']='PLN'
df['AVAILABILITY']='available'
df['LINK']=links
df['SHOP']='SzlachetneInwestycje'
df['IMG_LINK']=img_links
df['METAL']=metals
df['PRICE_PER_OZ_PLN'] = (df['PRICE']/df['OZ']).round(2)
df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].round(2).apply(lambda x: '%.2f' % x).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.',','))
df['PRICE_PLN']= (df['PRICE']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.',','))

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

cur.execute("DELETE from compare_app_pricings where SHOP = 'SzlachetneInwestycje'")
conn.commit()
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
  'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings', conn, if_exists='append', index=False, chunksize=1000)

try:
    conn.close()
except Exception as e:
    print(e)