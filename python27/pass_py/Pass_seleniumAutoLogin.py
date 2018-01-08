#encoding=utf8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
driver = webdriver.Chrome();driver.get("http://mail.163.com")
driver.switch_to.frame('x-URS-iframe')

elem_user = driver.find_element_by_name("email");elem_user.send_keys("chusiping")
elem_pwd = driver.find_element_by_name("password");elem_pwd.send_keys("pwd761110")
elem_pwd.send_keys(Keys.RETURN)
assert "baidu" in driver.title
driver.close();driver.quit()



# #encoding=utf8
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# import time
# driver = webdriver.Chrome();driver.get("http://www.renren.com/")
# elem_user = driver.find_element_by_name("email");elem_user.send_keys("15626169339")
# elem_pwd = driver.find_element_by_name("password");elem_pwd.send_keys("1qaz2wsx")
# elem_pwd.send_keys(Keys.RETURN)
# assert "baidu" in driver.title
# driver.close();driver.quit()