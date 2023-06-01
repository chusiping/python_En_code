from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
# 初始化
# def init():
chromeOptions = webdriver.ChromeOptions()
# 定义为全局变量，方便其他模块使用
global url, browser, username, password, wait
# 登录界面的url
url = 'https://oa.gzqiaoyin.com/login/Login.jsp?gopage=&_rnd_=42691d88-ae6b-45fe-a92d-684fd3f3f9fe'
# 实例化一个chrome浏览器
# d = webdriver.Chrome('/usr/bin/chromedriver')
browser = webdriver.Chrome('/usr/bin/chromedriver')
# chromeOptions.addArguments("--disable-extensions")
# chromeOptions.addArguments("--headless")
# chromeOptions.addArguments("--display-gpu")
# chromeOptions.addArguments("--no-sandbox")
# 用户名
username = '00119960'
# 密码
password = '1qaz@WSX'
# 设置等待超时
# wait = WebDriverWait(browser, 20)

# if __name__ == '__main__':
#     init() 