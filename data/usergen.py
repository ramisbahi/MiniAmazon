import os
import json
import gzip
import pandas as pd
from urllib.request import urlopen
import numpy as np

data = {'username' : [], 'is_seller' : ['TRUE'] * 99, 'bio' : ['a'] * 99, 'name' : [], 'password' : [], 'address' : []}

usernames = []
with open('users/sellers.txt') as f:
    for username in f.readlines():
        usernames.append(username.rstrip())
data['username'] = usernames

print(len(usernames))

names = []
with open('users/seller_names.txt') as f:
    for name in f.readlines():
        names.append(name.rstrip())
data['name'] = names

print(len(names))

passwords = []
with open('users/seller_passwords.txt') as f:
    for password in f.readlines():
        passwords.append(password.rstrip())
data['password'] = passwords
print(len(passwords))

addresses = []
with open('users/seller_addresses.txt') as f:
    while True:
        line1 = f.readline()
        if not line1:
            break
        line2 = f.readline()
        if not line2:
            break  # EOF
        addresses.append(line1 + line2)
data['address'] = addresses
print(len(addresses))

df = pd.DataFrame.from_dict(data)
df.to_csv('sellers.csv', index = False) # index false to get rid of unneeded columns
