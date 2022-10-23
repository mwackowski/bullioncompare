from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
from sqlalchemy import types, create_engine, sql
import json
import asyncio
import aiohttp

from db_path import DB_PATH
import sqlite3

nbpUrl = 'http://api.nbp.pl/api/exchangerates/rates/a/eur/'
jsonString = json.loads((requests.get(nbpUrl)).text)
currency = jsonString['code']
rateDate=jsonString['rates'][0]['effectiveDate']
rateVal=jsonString['rates'][0]['mid']


urls = {'silver':[],
       'gold': []}

page_urls = [
        ['1/10 oz',[0.1, 'https://goldsilver.be/en/104-110-oz']],
        ['1/4 oz', [0.25,'https://goldsilver.be/en/113-14-oz']],
        ['1/2 oz', [0.5, 'https://goldsilver.be/en/88-12-oz']],
        ['3/4 oz', [0.75,'https://goldsilver.be/en/105-34-oz']],
        ['1 oz' , [1,'https://goldsilver.be/en/84-1-oz-30-gr']],
        ['1 1/4 oz bizon', [1.25,'https://goldsilver.be/en/106-1-14-oz-bison']],
        ['1 1/2 oz', [1.5,'https://goldsilver.be/en/108-1-12-oz']],
        ['2 oz', [2,'https://goldsilver.be/en/95-2-oz-']],
        ['5 oz', [5, 'https://goldsilver.be/en/109-5-oz']],
        ['10 oz', [10, 'https://goldsilver.be/en/110-10-oz']],
        ['1 kg', [1000/31.1034768, 'https://goldsilver.be/en/111-kilo']],
        ['Monster box', [0,'https://goldsilver.be/en/134-monster-box']]]

for x in range(len(page_urls)):
    page_count=[]
    r = requests.get(page_urls[x][1][1])
    soup = bs(r.text, 'lxml')
    try:
        for last_page in soup.find('ul', class_='pagination').find_all('li'):
        #     print(last_page.text.strip() + ' ' + str(len(last_page.text.strip())) + ' ' + str(last_page.text.isnumeric()))
            try:
                page_count.append(int(last_page.text.strip()))
            except Exception as e:
                pass
    except Exception as e:
        page_count=[1]
    page_no = max(page_count)

    for y in range(1, page_no + 1):
        urls['silver'].append([page_urls[x][0], [page_urls[x][1][0], page_urls[x][1][1] +'?p=' + str(y)]])


page_urls = [
            ['1 oz', [1, 'https://goldsilver.be/en/18-1-oz-30gr-gold']],
            ['1/2 oz', [0.5, 'https://goldsilver.be/en/17-12-oz-gold']],
            ['1/4 oz', [0.25, 'https://goldsilver.be/en/16-14-oz-gold']],
            ['1/10 oz', [0.1, 'https://goldsilver.be/en/15-110-oz-gold']],
            ['1/20 oz', [0.05, 'https://goldsilver.be/en/14-120-oz-gold']]]

for x in range(len(page_urls)):
    page_count=[]
    r = requests.get(page_urls[x][1][1])
    soup = bs(r.text, 'lxml')
    try:
        for last_page in soup.find('ul', class_='pagination').find_all('li'):
        #     print(last_page.text.strip() + ' ' + str(len(last_page.text.strip())) + ' ' + str(last_page.text.isnumeric()))
            try:
                page_count.append(int(last_page.text.strip()))
            except Exception as e:
                pass
    except Exception as e:
        page_count=[1]
    page_no = max(page_count)

    for y in range(1, page_no + 1):
        urls['gold'].append([page_urls[x][0], [page_urls[x][1][0], page_urls[x][1][1] +'?p=' + str(y)]])


async def main():
    async with  aiohttp.ClientSession() as session:    
        tasks = []      
        for metal in ['silver', 'gold']:
            for x in range(len(urls[metal])):
                url = urls[metal][x][1][1]
                weight = str(urls[metal][x][0])
                weight_num = urls[metal][x][1][0]
                # print(url, weight, weight_num)
                task = asyncio.ensure_future(send_request(session, url, metal, weight, weight_num))
                tasks.append(task)
            results = await asyncio.gather(*tasks)                                  
        return results

async def send_request(session, url, metal, weight, weight_num):
    async with session.get(url, headers=header) as response:
        result_data = await response.read()
        return (result_data.decode(), metal, weight, weight_num)

header = {'Accept-Encoding': 'gzip', 'accept-language': '*'}

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
outcome = loop.run_until_complete(main())
# loop.close()


import time
weight, weight_num, names, prices, availability, links, img_links, price_val, price_curr, metals= ([] for i in range(10))

for x in outcome:
    soup = bs(x[0], 'lxml')
    for container in soup.find_all('div', class_='product-container'):
        try:
            p_name = container.find('a', class_='product-name')['title']
            img = container.find('img', class_='replace-2x img-responsive')['src']
            p_price = container.find('span', class_='price product-price').text.strip()
            p_availability = container.find('span', class_='availability').text
            p_link = container.find('a', class_='product-name')['href']
            p_availability = container.find('span', class_='availability').text
            if x[1] == 'silver':
                metals.append('Silver')
            else:
                metals.append('Gold')
            weight.append(x[2])
            weight_num.append(x[3])
            prices.append(p_price)
            names.append(p_name)
            availability.append(p_availability[:99])
            links.append(p_link)
            img_links.append(img)
            # print(p_name + ' :' + p_price + ' | ' + p_availability + ' | ' + p_link)
        except Exception as e:
#             print(container)
            print(e)

price_val = []
price_curr = []
for x in prices:
    price_val.append(x[:x.find('€')].replace(',','.').replace(' ',''))
    price_curr.append('€')

df=pd.DataFrame()
df['WEIGHT']=weight
df['OZ']=weight_num
df['NAME']=names
df['PRICE_TEXT']=prices
df['PRICE']=price_val
df['PRICE']=df['PRICE'].astype(float) *rateVal
df['PRICE_PER_OZ'] = (df['PRICE']/df['OZ']).round(2)
df['PRICE_PER_OZ'] = df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df['CURRENCY']=price_curr
df['AVAILABILITY']=availability
df['LINK']=links
df['SHOP']='GoldSilver'
df['IMG_LINK']=img_links
df['METAL']=metals
df['PRICE_PER_OZ_PLN'] = (df['PRICE']/df['OZ']).round(2)
df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].round(2).apply(lambda x: '%.2f' % x).replace('inf','-').astype(str).apply(lambda x: x+' zł' if x!='-' else x).apply(lambda x: x.replace('.',','))
df['PRICE_PLN']= (df['PRICE']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł' if x!='-' else x).apply(lambda x: x.replace('.',','))

import datetime
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

cur.execute("DELETE from compare_app_pricings where SHOP = 'GoldSilver'")
conn.commit()
df[df['AVAILABILITY'].apply(lambda x: x.strip())!='Out of stock']\
[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK',\
  'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']]\
.to_sql('compare_app_pricings', conn, if_exists='append', index=False, chunksize=1000)

try:
    conn.close()
except Exception as e:
    print(e)