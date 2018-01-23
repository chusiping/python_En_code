#coding=utf-8 测试通过： 调用cookie.txt，无验证即可登录 2017-12-31
import webbrowser,os,urllib2,  cookielib,os
def login():
    cooktxt = os.path.abspath('../temp/cookie.txt')
    if not os.path.exists(cooktxt):
        print 'cookie does not exists !'
        exit()
    cookie = cookielib.MozillaCookieJar(cooktxt)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    cookie.load(ignore_discard=True, ignore_expires=True)
    login_response = opener.open('http://www.renren.com/privacyhome.do')
    print login_response.info()
    fout = open("data.html", "w")
    fout.write(login_response.read())
    fout.close()
    webbrowser.open('data.html')
if __name__=='__main__':
    login()