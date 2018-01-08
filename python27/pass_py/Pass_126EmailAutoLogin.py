#coding=utf-8 测试通过：自动弹开浏览器输入账号密码登陆邮箱 2017-12-26
'''126邮箱登陆'''
from time import ctime,sleep
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WANGYI(unittest.TestCase):
    def setUp(self):
        print('开始测试')
        self.username = 'chusiping'  # 定义账号
        self.password = 'pwd761110'   #定义密码
        self.driver = webdriver.Chrome()
        # self.driver.maximize_window()
        self.base_url = "http://mail.163.com/"
        self.driver.get(self.base_url)
        sleep(5)

    def test_login(self):
        '''测试登陆126邮箱'''
        WebDriverWait(self.driver,10).until( EC.presence_of_element_located((By.ID, "x-URS-iframe")))
        self.driver.switch_to.frame("x-URS-iframe")  #切换进入frame 在这里也可以写self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="x-URS-iframe"]')),先定位元素
        self.driver.find_element_by_name("email").send_keys(self.username)
        self.driver.find_element_by_name("password").send_keys(self.password)
        self.driver.find_element_by_id("dologin").click()

        # WebDriverWait(self.driver,10).until( EC.presence_of_element_located((By.ID, "spnUid"))) #增加等待时间，判断验证信息元素是否显示
        # verifyLoginSucceed = self.driver.find_element_by_xpath('//*[@id="spnUid"]').text
        # self.assertIn(self.username,verifyLoginSucceed)    #验证是否登陆成功
    def tearDown(self):
        # self.driver.implicitly_wait(30)
        assert "baidu" in self.driver.title
        # self.driver.quit()
        print('测试结束')

if __name__ == '__main__':
    unittest.main()