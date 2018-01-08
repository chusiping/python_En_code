#coding=utf-8 测试通过：selenium自动登录163邮箱 2017-12-27
from selenium import webdriver
from time import sleep
driver = webdriver.Chrome()
#最大化窗口
# driver.maximize_window()
driver.get('http://mail.163.com/')
sleep(2)
#切换到表单
driver.switch_to.frame("x-URS-iframe")
driver.find_element_by_name("email").clear()
driver.find_element_by_name("email").send_keys('chusiping')
driver.find_element_by_name("password").clear()
driver.find_element_by_name("password").send_keys('pwd761110')
driver.find_element_by_id("dologin").click()