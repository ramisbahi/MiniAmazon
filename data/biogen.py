import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--enable-javascript")
driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)
driver.get('http://www.generatorland.com/glgenerator.aspx?id=124')
genButton = driver.find_elements_by_xpath('//*[@id="lblCode"]/div/div[3]/a')

for i in range(0, 5):
    genButton[0].click()

    time.sleep(0.5)
    result = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(result, 'html.parser')
    text = soup.find('div', id ='menu_item1').text
    print(text)
