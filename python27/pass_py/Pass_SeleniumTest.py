#coding=utf-8 测试通过：调用不同浏览器打开url地址 2017-12-26
from selenium import webdriver
driver = webdriver.PhantomJS()
driver.get("http://www.baidu.com/")
data = driver.title
print data



# from selenium import webdriver
# browser = webdriver.Chrome()
# browser.get('http://www.baidu.com/')



# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
#
# driver = webdriver.Chrome("D:\Python27\chromedriver.exe")
# driver.get("http://www.python.org")
# assert "Python" in driver.title
# elem = driver.find_element_by_name("q")
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# print driver.page_source



#
# import unittest
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
#
# class PythonOrgSearch(unittest.TestCase):
#
#     def setUp(self):
#         self.driver = webdriver.Chrome("D:\Python27\chromedriver.exe")
#
#     def test_search_in_python_org(self):
#         driver = self.driver
#         driver.get("http://www.python.org")
#         self.assertIn("Python", driver.title)
#         elem = driver.find_element_by_name("q")
#         elem.send_keys("pycon")
#         elem.send_keys(Keys.RETURN)
#         assert "No results found." not in driver.page_source
#
#     def tearDown(self):
#         self.driver.close()
#
# if __name__ == "__main__":
#     unittest.main()