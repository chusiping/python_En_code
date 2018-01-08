# coding:utf-8
# 测试通过可以获得IP,目前缺少端口  2017-12-22
from fake_useragent import UserAgent
import urllib
import urllib2
import requests
import re
from bs4 import BeautifulSoup
from time import ctime,sleep
htmlall = ''
class Items(object):
    IP = None
    Port = None
    Add = None
    Type = None

values = {}
url_domain='http://www.kuaidaili.com/'
url = url_domain + 'free/intr/1'

###################一个网址进行循环#########################
targets = []
for i in range(1,4):
    target = r"http://www.kuaidaili.com/free/intr/%d" %i
    targets.append(target)
    # print (targets)
###########################################################
headers = {  'User-Agent': UserAgent().random ,'Referer':url_domain }
data = urllib.urlencode(values)

for url in targets:
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    html = response.read()
    htmlall = htmlall + html
    sleep(1)

soup = BeautifulSoup(htmlall,'lxml')
trs = soup.find_all('tr')
items = []
sum_agent = 0
for tr in trs:
    if tr.find('td'):
        tds = tr.find_all('td')
        item = Items()
        item.IP = tr.find_all('td')[0].get_text().strip()
        item.Port = tr.find_all('td')[1].get_text().strip()
        # item.Add = tr.find_all('td')[3].get_text().strip()
        # item.Type = tr.find_all('td')[5].get_text().strip()
        # print item.IP + ':' + item.Port
        sum_agent += 1
        items.append(item.IP + ':' + item.Port)
# print html

# ips=re.findall("(?isu)\d+\.\d+\.\d+\.\d+",html)
# print  ips
# if ips: open("ips.txt","wb").write("\r\n".join(ips))
##############################写入文件##############################
fileObject = open('ips.txt', 'wb')
for ip in items:
    fileObject.write(ip)
    fileObject.write('\n')
fileObject.close()
############################################################
##############################检测代理是否有效-###################################
for ip in items:
    try:
        requests.get('http://www.baidu.com/', proxies={"http": 'http://'+ip})
    except:
        print ip + ' failed'
    else:
        print ip + ' success'
##################################################################################

        # #-------------star------------------------
# from fake_useragent import UserAgent
# ua = UserAgent()
# print(ua.random)
# print(ua.random)
# print(ua.random)
# #-------------End-------------------------

#-------------------------version 测试版本带冗余代码--------------------------------------------
# # coding:utf-8
# # 测试通过可以获得IP,目前缺少端口  2017-12-22
# from fake_useragent import UserAgent
# import urllib
# import urllib2
# import re
#
# # values = {'name' : 'WHY','location' : 'SDU', 'language' : 'Python' }
# values = {}
#
# # url='http://www.baidu.com/'
#
# url_domain='http://www.kuaidaili.com/'
# url = url_domain + 'free/inha/'
#
# # url_domain='http://www.xicidaili.com/'
# # url = url_domain + 'nn/2'
#
# headers = {  'User-Agent': UserAgent().random ,'Referer':url_domain }
# data = urllib.urlencode(values)
# req = urllib2.Request(url, data, headers)
#
# ##--------------------------------------------------------
# # httpHandler = urllib2.HTTPHandler(debuglevel=1)
# # httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
# # opener = urllib2.build_opener(httpHandler, httpsHandler)
# # urllib2.install_opener(opener)
# ##________________________________________________________
#
#
# # try:
# #     response = urllib2.urlopen(req)
# # except urllib2.HTTPError, e:
# #     print e.code
#
#
# html = response.read()
# # print html
# ips=re.findall("(?isu)\d+\.\d+\.\d+\.\d+",html)
# print  ips
# if ips: open("ips.txt","wb").write("\r\n".join(ips))
#
#
#
#
#
# # #-------------star------------------------
# # from fake_useragent import UserAgent
# # ua = UserAgent()
# # print(ua.random)
# # print(ua.random)
# # print(ua.random)
# # #-------------End-------------------------