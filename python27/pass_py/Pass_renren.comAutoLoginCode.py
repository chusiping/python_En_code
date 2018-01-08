#encoding=utf8 测试通过：人人网自动登陆脚本  2017-12-24
import urllib2, urllib, cookielib
urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()),urllib2.HTTPHandler()))
# email='15626169339';password='1qaz2wsx';domain='renren.com';url='http://www.renren.com/PLogin.do'
email='chusiping@sohu.com';password='pwd123456';domain='csdn.net'
url='https://passport.csdn.net/account/verify;jsessionid=CC988806EAD32E0B1425495DF6809075.tomcat2'


headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0'}
data={'email' : email, 'password' : password,'domain': domain }
postdata = urllib.urlencode(data)
req=urllib2.Request(url,postdata,headers)
rt_html = urllib2.urlopen(req).read()
print rt_html
if '手机绑定' in rt_html:
    print '登录成功！'
else:
    print '失败！'
