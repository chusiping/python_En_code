#coding=utf-8 测试通过：抓取某站的代理ip，返回一个数组  2018-1-25
from lib import deflibs
r = deflibs.RequestsGet('http://www.data5u.com/free/gngn/index.shtml')
ips=[];idx=[0]
arr_ip= deflibs.GetProxyIpFromTag(r.text,idx,ips)
print ips

proxies = {  "http": "http://221.7.255.167:8080",  "https": "http://218.241.234.48:8080",}
r = deflibs.RequestsGetByProxy('http://www.winshang.com/index.html',proxies)
print r.text

