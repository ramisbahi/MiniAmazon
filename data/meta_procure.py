import os
import json
import gzip
import pandas as pd
from urllib.request import urlopen
import numpy as np


category = 'Tools_and_Home_Improvement' # change category to generate csv from meta_<category>.json
category_name = category
category_name = 'Tools and Home Improvement' # custom name in "category" column


data = []
with open('metadata/meta_' + category + '.json') as f:
    for l in f:
        data.append(json.loads(l.strip()))

df = pd.DataFrame.from_dict(data)

### remove rows with unformatted title (i.e. some 'title' may still contain html style content)

df = df.dropna()

df = df[~df.title.str.contains('getTime')] # filter those unformatted rows
df = df.drop(columns=['tech1', 'tech2', 'similar_item', 'fit', 'also_buy', 'brand', 'feature', 'rank', 'also_view', 'details', 'main_cat', 'date'])

df = df[df.price.str.startswith('$')] # only valid prices (cannot be null)
df['price'] = df.price.str.slice(start=1)
df['price'] = df.price.str.replace(',', '', regex=False) # get rid of commas in price
df['price'] = df.price.apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna().astype(float) # make sure floats only
df = df[df['price'].notna()]

df['description'] = df.description.apply(lambda x: x[0] if len(x) > 0 else '') # first element of description list
df = df[df['description']!='']
df['description'] = df.description.str.slice(start = 0, stop = 1990) # ~ 2000 character limit

df['image'] = df.image.apply(lambda x: x[0][:len(x[0])-5] + "0_.jpg" if len(x) > 0 and 'SS40' in x[0] else '') # make image first url, make 400px
df = df[df['image']!='']

df = df.rename(columns={"asin" : "product_id", "title" : "item_name"})

df['item_name'] = df.item_name.str.slice(start = 0, stop = 490) # ~ 500 character limit
df = df[df['item_name'] != '']

df['category'] = category_name

df = df.groupby('product_id').apply(lambda df: df.sample(1)) # one of each product_id

#df = df.head(50) # delete later

conditions = ['New', 'Used - Like New', 'Used - Very Good', 'Used - Good', 'Used - Acceptable']

names1 = []
with open('users/sellers1.txt') as f:
    for name in f.readlines():
        names1.append(name.rstrip())
df['seller_username'] = np.random.choice(names1, len(df)) # choose random usernames from list 1
df['quantity'] = np.random.randint(1,50, size=len(df))
df['condition'] = np.random.choice(conditions, len(df), p=[0.5, 0.2, 0.1, 0.1, 0.1])

df2 = df.copy(deep = True) # copy with different usernames and quantities
names2 = []
with open('users/sellers2.txt') as f:
    for name in f.readlines():
        names2.append(name.rstrip())
df2['seller_username'] = np.random.choice(names2, len(df2)) # choose random usernames from list 2
df2['quantity'] = np.random.randint(1,50, size=len(df2))
df2['condition'] = np.random.choice(conditions, len(df2), p=[0.5, 0.2, 0.1, 0.1, 0.1])

df3 = df.copy(deep = True) # copy with different usernames and quantities
names3 = []
with open('users/sellers3.txt') as f:
    for name in f.readlines():
        names3.append(name.rstrip())
df3['seller_username'] = np.random.choice(names3, len(df3))
df3['quantity'] = np.random.randint(1,50, size=len(df3))


df = pd.concat([df, df2])
df = pd.concat([df, df3])

df.to_csv('meta_' + category + '.csv', index = False) # index false to get rid of unneeded columns
