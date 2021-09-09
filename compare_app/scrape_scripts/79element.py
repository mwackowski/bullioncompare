#!/usr/bin/env python
# coding: utf-8

# In[46]:


from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from sqlalchemy import types, create_engine, sql
import re
import numpy as np
import json, datetime
elementUrlsGold = {'1 oz': 'https://79element.pl/zlote-monety-inwestycyjne-1oz/',
                    '1/2 oz': 'https://79element.pl/zlote-monety-inwestycyjne-12oz/',
                    '1/4 oz': 'https://79element.pl/zlote-monety-inwestycyjne-14oz/',
                    '1/10 oz': 'https://79element.pl/zlote-monety-inwestycyjne-110oz/'}
elementUrlsSilver = 'https://79element.pl/srebrne-monety-bulionowe/'


# In[47]:


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
    exclude_list = ['pakiet', 'zł', 'dukat', 'zestaw']
    value = None
    found = False
    for excluded in exclude_list:
        if re.search(rf"\b{excluded}\b", x, re.IGNORECASE):
            value = (0, 'other')
            break;
        else:
            for a in weights_dict:
                if re.search(rf"\b{a}g\b", x, re.IGNORECASE) or re.search(rf"\b{a} g\b", x, re.IGNORECASE) or                 re.search(rf"\b{a}gram\b", x, re.IGNORECASE) or re.search(rf"\b{a}grams\b", x, re.IGNORECASE) or                 re.search(rf"\b{a} gram\b", x, re.IGNORECASE) or re.search(rf"\b{a} grams\b", x, re.IGNORECASE) or re.search(rf"\b{a} gramów\b", x, re.IGNORECASE):
                    value = (weights_dict[a], 'g')
                elif re.search(rf"\b{a}kilo\b", x, re.IGNORECASE) or re.search(rf"\b{a}kg\b", x, re.IGNORECASE) or                 re.search(rf"\b{a} kilo\b", x, re.IGNORECASE) or re.search(rf"\b{a} kg\b", x, re.IGNORECASE):
                    value = (weights_dict[a], 'kg')
                elif re.search(rf"\b{a}oz\b", x, re.IGNORECASE) or re.search(rf"\b{a} oz\b", x, re.IGNORECASE):
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


# In[48]:


def find_price(price):
    price_val = (price[:price.find('zł')].strip().replace(' ','').replace(',','.'))
    return float(price_val)


# In[49]:


# weights_dict = {'1oz': 1, '1/2oz': }
weights, weight_nums, names, prices, availability, links, img_links, price_val, metals= ([] for i in range(9))

for k, v in elementUrlsGold.items():
    r = requests.get(v)
    soup = bs(r.text, 'lxml')
    products = soup.find_all('li', class_='ajax_block_product')
    for product in products:
        if product.find('a', class_='button ajax_add_to_cart_button exclusive') != None:
            h5 = product.find('h5')
            names.append(h5.text)
            links.append(h5.a['href'])
            img_links.append(product.img['src'])
            price = product.find('span', class_='price').text
            prices.append(price)
            price_val.append(find_price(price))
            weights.append(k)
            metals.append('Gold')
            weight_nums.append(float(find_weight(k)[1]))

#             print(name, link, img, prices, price_val, weight, find_weight(weight))


# In[50]:


# weights_dict = {'1oz': 1, '1/2oz': }

r = requests.get('https://79element.pl/srebrne-monety-bulionowe/')
soup = bs(r.text, 'lxml')
products = soup.find_all('li', class_='ajax_block_product')
for product in products:
    if product.find('a', class_='button ajax_add_to_cart_button exclusive') != None:
        h5 = product.find('h5')
        names.append(h5.text)
        links.append(h5.a['href'])
        img_links.append(product.img['src'])
        price = product.find('span', class_='price').text
        prices.append(price)
        price_val.append(find_price(price))
        weight = find_weight(h5.text)
        weights.append(weight[0])
        metals.append('Silver')
        weight_nums.append(float(weight[1]))
        # print(h5.text, h5.a['href'], find_weight(h5.text) )



# In[51]:


df=pd.DataFrame()
df['WEIGHT']=weights
df['OZ']=weight_nums
df['NAME']=names
df['PRICE_TEXT']=prices
df['PRICE_TEXT'] = df['PRICE_TEXT'].apply(lambda x: x.replace(' ', ''))
df['PRICE']=price_val

df['CURRENCY']='PLN'
df['AVAILABILITY']='available'
df['LINK']=links
df['SHOP']='79thElement'
df['IMG_LINK']=img_links
df['METAL']=metals


# In[52]:


df=pd.DataFrame()
df['WEIGHT']=weights
df['OZ']=weight_nums
df['NAME']=names
df['PRICE_TEXT']=prices
df['PRICE_TEXT'] = df['PRICE_TEXT'].apply(lambda x: x.replace('zł', 'PLN')).apply(lambda x: x.replace('\u0142',''))
df['PRICE']=price_val
df['PRICE_PER_OZ'] = (df['PRICE']/df['OZ']).round(2)
df['PRICE_PER_OZ'] = df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df['CURRENCY']='PLN'
df['AVAILABILITY']='available'
df['LINK']=links
df['SHOP']='79thElement'
df['IMG_LINK']=img_links
df['METAL']=metals
df['PRICE_PER_OZ_PLN'] = (df['PRICE']/df['OZ']).round(2)
df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].round(2).apply(lambda x: '%.2f' % x).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.',','))
df['PRICE_PLN']= (df['PRICE']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.',','))

data_dzis = datetime.datetime.now().strftime('%Y-%m-%d')
data_godzina = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df['LOAD_TIME'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# In[53]:


dtype = {c:types.VARCHAR(df[c].str.len().max())
        for c in df.columns[df.dtypes == 'object'].tolist()}
db_string_mysql = 'mysql://wladzioo:Mnop)(!@#@wladzioo.mysql.eu.pythonanywhere-services.com:3306/wladzioo$testdb?charset=utf8'
engine = create_engine(db_string_mysql, pool_recycle=280)
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK', 'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']].to_sql('compare_app_pricings_all', engine, if_exists='append', index=False, dtype=dtype, chunksize=1000)


# In[54]:


from sqlalchemy import text
with engine.connect().execution_options(autocommit=True) as conn:
    conn.execute(text("DELETE from compare_app_pricings where SHOP = '79thElement'"))
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK', 'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']].to_sql('compare_app_pricings', engine, if_exists='append', index=False, dtype=dtype, chunksize=1000)
