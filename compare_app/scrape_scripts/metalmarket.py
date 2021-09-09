#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from sqlalchemy import types, create_engine, sql
import re
import numpy as np
import json
import datetime
import math


# In[2]:


metalmarketurls= ['https://www.metalmarket.eu/sw/menu/monety/srebrne-monety-851.html',
                  'https://www.metalmarket.eu/sw/menu/monety/zlote-monety-850.html']


# In[3]:


metalmarketurspaged=[]
for x in range(len(metalmarketurls)):
    r = requests.get(metalmarketurls[x])
    soup = bs(r.text, "lxml")

    total_pages = soup.find('span', class_='navigation_total').find('b').text

    pages = math.ceil(int(total_pages.strip())/30)

    for page in range(pages):
        if x == 0:
            metalmarketurspaged.append('https://www.metalmarket.eu/sw/menu/monety/srebrne-monety-851.html?counter=' + str(page))
        else:
            metalmarketurspaged.append('https://www.metalmarket.eu/sw/menu/monety/zlote-monety-850.html?counter=' + str(page))


# In[4]:


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
                  'inne': {0: 'inne'}
                  }
    exclude_list = ['pakiet', 'zł', 'zestaw', '5 Euro', '10 Euro', '20 Euro', '100 Euro', '50 Euro']
    value = None
    found = False
    for excluded in exclude_list:
        if re.search(rf'\b{excluded}\b', x, re.IGNORECASE):
            value = (0, 'inne')
            break;
        else:
            for a in weights_dict:
                if re.search(rf'\b{a}g\b', x, re.IGNORECASE) or re.search(rf'\b{a} g\b', x, re.IGNORECASE) or                 re.search(rf'\b{a}gram\b', x, re.IGNORECASE) or re.search(rf'\b{a}grams\b', x, re.IGNORECASE) or                 re.search(rf'\b{a} gram\b', x, re.IGNORECASE) or re.search(rf'\b{a} grams\b', x, re.IGNORECASE) or re.search(rf'\b{a} gramów\b', x, re.IGNORECASE):
                    value = (weights_dict[a], 'g')
                elif re.search(rf'\b{a}kilo\b', x, re.IGNORECASE) or re.search(rf'\b{a}kg\b', x, re.IGNORECASE) or                 re.search(rf'\b{a} kilo\b', x, re.IGNORECASE) or re.search(rf'\b{a} kg\b', x, re.IGNORECASE):
                    value = (weights_dict[a], 'kg')
                elif re.search(rf'\b{a}oz\b', x, re.IGNORECASE) or re.search(rf'\b{a} oz\b', x, re.IGNORECASE):
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
                        value = (0, 'inne')

    if value[1] == 'g':
        weight_in_oz = value[0]/31.1034768
    elif value[1] == 'kg':
        weight_in_oz = value[0]*1000/31.1034768
    elif value[1] == 'inne':
        weight_in_oz = 0
    else:
        weight_in_oz = value[0]
    if value[1] == 'inne':
        return_string = (value[1], str(weight_in_oz))
    else:
        return_string = (rev_weight_dict[value[1]][value[0]], str(weight_in_oz))
    return return_string





def find_price(price):
    price_val = price.replace('\xa0', ' ')
    price_val = (price_val[:price_val.find('zł')].strip().replace(' ','').replace(',','.'))
    return price_val

def find_img(link):
    r = requests.get(link)
    soup = bs(r.text, "lxml")
    print(soup.find('div', class_='photos col-md-6 col-xs-12').find('img', class_='photo')['src'])

######

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")


driver = webdriver.Chrome(options=chrome_options)
driver.delete_all_cookies()


def get_html(url, driver):
    driver.get(url)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[contains(@class, "b-lazy b-loaded")]')))
    scroll_pause_time = 1
    screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    i = 1
    while True:

        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        i += 1
        time.sleep(scroll_pause_time)
        scroll_height = driver.execute_script("return document.body.scrollHeight;")
        if (screen_height) * i > scroll_height:
            break

    html = driver.page_source

    return html
######

weights, weight_nums, names, prices, availability, links, img_links, price_val, price_curr, metals= ([] for i in range(10))

for x in range(len(metalmarketurspaged)):
   # r = requests.get(metalmarketurspaged[x])
   # soup = bs(r.text, "lxml")
    html =  get_html(metalmarketurspaged[x], driver)
#     r = requests.get(metalmarketurspaged[x])
    soup = bs(html, 'lxml')

    for product in soup.find_all('div', class_='product_wrapper'):
        link = 'https://metalmarket.eu' + product.find('a', class_='product-icon align_row')['href']
        name = product.find('a', class_='product-name').text
        name = name.replace('uncja', 'oz').replace('uncje', 'oz').replace('uncji', 'oz').replace('Uncji', 'oz').replace('Uncja', 'oz').replace('Uncje', 'oz')
        price = product.find('div', class_='product_prices').text.strip()
        img = 'https://metalmarket.eu' + product.find('img', class_='b-lazy b-loaded')['src']
        if price.strip() == 'Cena na telefon':
            price_val.append('Cena na telefon')
            price_curr.append('')
        else:
            price_val.append(find_price(price))
            price_curr.append('zł')
        weight = find_weight(name)[0]
        weight_num = float(find_weight(name)[1])
        weights.append(weight)
        weight_nums.append(weight_num)

        links.append(link)
        img_links.append(img)
        names.append(name)

        prices.append(price)

        if metalmarketurspaged[x].find('srebrne') > 0:
            metal = 'Silver'
        else: metal = 'Gold'
        metals.append(metal)
        #try:
        #print(name, link, find_price(price), weight, metal)
       # except Exception as e:
        #    print(e)


# In[7]:


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


# In[8]:


df1 = df[df['PRICE']!='Cena na telefon']


# In[9]:


df1['PRICE'] = df1['PRICE'].astype(np.float64)
df1['PRICE_PER_OZ'] = (df1['PRICE']/df1['OZ']).round(2)
df1['PRICE_PER_OZ'] = df1['PRICE_PER_OZ'].replace(np.inf,'-').astype(str)
df1['PRICE_PER_OZ_PLN'] = (df1['PRICE']/df1['OZ']).round(2)
df1['PRICE_PER_OZ_PLN'] = df1['PRICE_PER_OZ_PLN'].round(2).apply(lambda x: '%.2f' % x).replace('inf','-').astype(str).apply(lambda x: x+' zł' if x!='-' else x).apply(lambda x: x.replace('.',','))
df1['PRICE_PLN']= (df1['PRICE']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł' if x!='-' else x).apply(lambda x: x.replace('.',','))

data_dzis = datetime.datetime.now().strftime('%Y-%m-%d')
data_godzina = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df1['LOAD_TIME'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# In[10]:


dtype = {c:types.VARCHAR(df[c].str.len().max())
        for c in df.columns[df.dtypes == 'object'].tolist()}
#df1[['WEIGHT', 'NAME', 'PRICE', 'PRICE_PER_OZ', 'PRICE_PLN', 'PRICE_PER_OZ_PLN', 'CURRENCY', 'AVAILABILITY', 'LINK', 'SHOP', 'IMG_LINK']].to_excel('C:\\Users\\user\\Desktop\\srebro\\metalmarket_'+data_dzis+'.xlsx', index=False)
#df1.to_excel('C:\\Users\\user\\Desktop\\srebro\\metalmarket_full_'+data_dzis+'.xlsx', index=False)


# In[11]:


#db_string_mysql = 'mysql://root:Djngblnapp!@#@127.0.0.1:3306/testdb?charset=utf8'
db_string_mysql = 'mysql://wladzioo:Mnop)(!@#@wladzioo.mysql.eu.pythonanywhere-services.com:3306/wladzioo$testdb?charset=utf8'
engine = create_engine(db_string_mysql, pool_recycle=280)
df1[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK', 'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']].to_sql('compare_app_pricings_all', engine, if_exists='append', index=False, dtype=dtype, chunksize=1000)


# In[12]:


from sqlalchemy import text
with engine.connect().execution_options(autocommit=True) as conn:
    conn.execute(text("DELETE from compare_app_pricings where SHOP = 'MetalMarket'"))
df1[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK', 'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']].to_sql('compare_app_pricings', engine, if_exists='append', index=False, dtype=dtype, chunksize=1000)

try:
    engine.dispose()
    conn.close()
except Exception as e:
    print(e)