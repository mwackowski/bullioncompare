#!/usr/bin/env python
# coding: utf-8

# In[359]:


from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
from sqlalchemy import types, create_engine, sql
import json
import math
import os

# In[370]:


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
    try:
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, 'uc-btn-accept-banner'))).click()
        time.sleep(3)
    except Exception as e:
        pass
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="product-img"]')))
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="product-id-stock"]')))

    html = driver.page_source

    return html


def find_price(x):
    return float(x.split()[0].replace('.','').replace(',','.'))


def get_links(html, metal, weight, weight_text):

    links = []
    soup = bs(html, 'lxml')
    for x in soup.find_all('div', class_='product-tile'):
        try:
            try:
                link = x.find('a', class_='hyp-thumbnail')['href']
                img = x.find('a', class_='hyp-thumbnail').find('img', class_='fl-active-img')['src']
                custom_title = x.find('div', class_='custom-title').text.strip()
                name = x.find('a', class_='product-title').text.strip() + ' ' + custom_title
            except Exception as e:
                print('linki: ' + e)
            try:
                availability = x.find('div', class_='product-id-stock').text.strip()
            except Exception as e:
                print('blad dostepnosci ' + e)
            metal = metal
            for p in x.find_all('span', class_='prices'):
                try:
                    price = p.get_text(strip=True, separator='|').split('|')[-1]

                    price_val = find_price(price)
                except Exception as e:
                    price = 0
                    price_val = 0
            links.append([name, link, img, weight, weight_text, price, price_val, availability, metal])
         #   print(f'{name} {weight_text} {price}: {price_val}, {link} , {img} {availability}' )

        except Exception as e:
            print(e)
    return links


# In[372]:


first = 0
urls = {'silver': [
              ['1 oz', [1, f'https://www.emk.com/en-us/silver/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fsilver&attrib%5BUNZENGEWICHT%5D%5B0%5D=1&first=']],
              ['1/2 oz', [0.5, f'https://www.emk.com/en-us/silver/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fsilver&attrib%5BUNZENGEWICHT%5D%5B0%5D=0%2C5&first=']],
              ['2 oz', [2, f'https://www.emk.com/en-us/silver/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fsilver&attrib%5BUNZENGEWICHT%5D%5B0%5D=2&first=']],
              ['5 oz', [5, f'https://www.emk.com/en-us/silver/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fsilver&attrib%5BUNZENGEWICHT%5D%5B0%5D=5&first=']]
                ],
        'gold': [
                ['1 oz', [1, 'https://www.emk.com/en-us/gold/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fgold&attrib%5BUNZENGEWICHT%5D%5B0%5D=1&first=']],
                ['1/2 oz', [0.5, 'https://www.emk.com/en-us/gold/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fgold&attrib%5BUNZENGEWICHT%5D%5B0%5D=0%2C5&first=']],
                ['1/4 oz', [0.25, 'https://www.emk.com/en-us/gold/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fgold&attrib%5BUNZENGEWICHT%5D%5B0%5D=0%2C25&first=']],
                ['1/10 oz', [0.1, 'https://www.emk.com/en-us/gold/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fgold&attrib%5BUNZENGEWICHT%5D%5B0%5D=0%2C1&first=']]

        ]
}


count = 0
first = 0
all_links = []

#url = f'https://www.emk.com/en-us/silver/#navigation:q=&attrib%5Bcat_url%5D%5B0%5D=%2Fsilver&attrib%5BUNZENGEWICHT%5D%5B0%5D=1&order=shopsort+desc&first={first}'
for metal in ['silver', 'gold']:
    for page in range(len(urls[metal])):

        first = 0
        finished = False
        while not finished:
            try:
                os.system('rm -rf /tmp* >/dev/null 2>&1')
            except Exception as e:
                pass
            url = urls[metal][page][1][1] + str(first)
            # print(url)

            # print(f"waga: {urls[metal][page][0]}")
            try:
                try:
                    html_page = get_html(url, driver)
                except Exception as e:
                    print(e)
                    driver.quit()
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-gpu")
                    driver = webdriver.Chrome(options=chrome_options)
                    time.sleep(0.5)
                    html_page = get_html(url, driver)

                links = get_links(html_page, metal, weight = urls[metal][page][1][0], weight_text = urls[metal][page][0])

                if len(links)!=0:
                    all_links.extend(links)
                    first += 24
                    url = urls[metal][page][1][1] + str(first)
                    count+=1
                else:
                    break
                print(count)

            except Exception as e:
                print(e)
                finished = True


# In[331]:


weight, weight_num, name, price_text, price, availability, link, img_link, metal = ([] for i in range(9))
for x in all_links:
    weight.append(x[4])
    weight_num.append(x[3])
    name.append(x[0])
    price_text.append(x[5])
    price.append(x[6])
    availability.append(x[7])
    link.append(x[1])
    img_link.append(x[2])
    metal.append(x[8])


# In[319]:


all_links[1]


# In[306]:


nbpUrl = 'http://api.nbp.pl/api/exchangerates/rates/a/eur/'
jsonString = json.loads((requests.get(nbpUrl)).text)
currency = jsonString['code']
rateDate=jsonString['rates'][0]['effectiveDate']
rateVal=jsonString['rates'][0]['mid']


# In[332]:


import datetime
import locale
data_dzis = datetime.datetime.now().strftime('%Y-%m-%d')
data_godzina = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

locale.setlocale(locale.LC_ALL, '')
locale._override_localeconv = {'mon_thousands_sep': '.'}

df=pd.DataFrame()
df['WEIGHT']=weight
df['OZ']=weight_num
df['NAME']=name
df['PRICE_TEXT']=price_text
df['PRICE']=price
df['PRICE']=df['PRICE'] *rateVal
df['PRICE_PER_OZ'] = (df['PRICE']/df['OZ']).round(2)
# df['PRICE_PER_OZ'] = df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df['CURRENCY']='€'
df['AVAILABILITY']=availability
df['LINK']=link
df['SHOP']='Emk'
df['IMG_LINK']=img_link
df['METAL']=metal
df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ'].astype(float)
df['PRICE_PER_OZ']= df['PRICE_PER_OZ'].replace(np.inf,'n/a').astype(str)
df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].round(2).apply(lambda x: '%.2f' % x).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.',','))
# df['PRICE_PER_OZ_PLN'] = (df['PRICE']/df['OZ']).round(2).apply(lambda x: '%.2f' % x).astype(str).apply(lambda x: x+' zł').apply(lambda x: x.replace('.',','))
# df['PRICE_PER_OZ_PLN'] = df['PRICE_PER_OZ_PLN'].apply(lambda x: locale.format_string('%.2f', x, grouping=True, monetary=True)).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.', ' '))
df['PRICE_PLN']= df['PRICE'].round(2).apply(lambda x: '%.2f' % x).replace('inf','n/a').astype(str).apply(lambda x: x+' zł' if x!='n/a' else x).apply(lambda x: x.replace('.', ','))
df['LOAD_TIME'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# In[335]:


dtype = {c:types.VARCHAR(df[c].str.len().max())
        for c in df.columns[df.dtypes == 'object'].tolist()}
db_string_mysql = 'mysql://wladzioo:Mnop)(!@#@wladzioo.mysql.eu.pythonanywhere-services.com:3306/wladzioo$testdb?charset=utf8'
engine = create_engine(db_string_mysql, pool_recycle=280)
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK', 'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']].to_sql('compare_app_pricings_all', engine, if_exists='append', index=False, dtype=dtype, chunksize=1000)


# In[346]:


from sqlalchemy import text
with engine.connect().execution_options(autocommit=True) as conn:
    conn.execute(text("DELETE from compare_app_pricings where SHOP = 'EMK'"))
df =df[(~df['AVAILABILITY'].apply(lambda x: x.strip()).isin(['Out of stock', 'Currently not available']))]
df = df[df['PRICE']!=0]
df[['NAME', 'WEIGHT', 'OZ', 'PRICE_TEXT', 'PRICE_PER_OZ', 'CURRENCY', 'AVAILABILITY', 'LINK', 'PRICE', 'LOAD_TIME', 'SHOP', 'IMG_LINK','METAL', 'PRICE_PLN', 'PRICE_PER_OZ_PLN']].to_sql('compare_app_pricings', engine, if_exists='append', index=False, dtype=dtype, chunksize=280)

try:
    engine.dispose()
    conn.close()
    driver.quit()
except Exception as e:
    print(e)