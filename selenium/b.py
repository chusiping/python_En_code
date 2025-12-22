#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

s = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=s)
driver.get('https://www.baidu.com')
driver.close()



# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument('--no-sandbox')
# driver = webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options)
# driver.get('http://www.google.com')
# print('test')
# driver.close()