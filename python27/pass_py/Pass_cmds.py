#coding=utf-8 测试通过：常用命令
import os
import sys,time
from urllib2 import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup

print '1. '+ str(os.path.exists('../ip.txt'))  #文件存在否
print '2. '+ str(os.path.abspath('../ip.txt')) #文件路径
print '3. 参数个数为:', len(sys.argv), '个参数。' #命令参数个数
print '   参数列表:', str(sys.argv) # 命令参数数组列表
print '4. http://t.cn/zQb28uh is ' + urlopen(Request('http://t.cn/zQb28uh')).geturl()
print '5. '+ time.strftime('%Y_%m%d_%H%M%S_',time.localtime(time.time()))
print '6. ' + os.path.basename('http://www.sharejs.com/images/logo.gif')

######################################################################
if len(sys.argv)>1:
    print str(sys.argv[1])
# os.remove('../temp/ip.txt')
if not os.path.exists('../temp/'):
    os.makedirs('../temp/')
#######################################################################
html = '''<html><head><title>The Dormouse's story</title></head><body>
<p class="title"><b>The Dormouse's story</b></p><p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;and they lived at the bottom of a well.</p>
<p class="story">...</p>'''
soup = BeautifulSoup(html,'lxml')
rt = soup.find_all('p')
print rt
# print(soup.prettify())
# print(soup.title)
# print(soup.title.name)
# print(soup.title.string)
# print(soup.title.parent.name)
# print(soup.p)
# print(soup.p["class"])
# print(soup.a)
# print(soup.find_all('a'))
# print(soup.find(id='link3'))