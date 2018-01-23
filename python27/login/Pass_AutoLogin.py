#coding=utf-8 测试通过：人人网自动登陆，保存登陆后的主页
#                       注意多次登陆被提示验证码
import webbrowser,os
import urllib2, urllib, cookielib
login_url = 'http://www.renren.com/PLogin.do'
data_url ='http://safe.renren.com/security/account'
email = '15626169339'
password = '1qaz2wsx'
domain='renren.com'

def login():
    cj =cookielib.CookieJar()
    opener =urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    LoginData = {
       'email':email,
       'password':password,
       'domain':domain,
       };
    login_req =urllib2.Request(login_url, urllib.urlencode(LoginData));
    login_req.add_header('User-Agent', "Mozilla/5.0 (X11; Ubuntu; Linuxx86_64; rv:31.0) Gecko/20100101 Firefox/31.0");
    login_response=opener.open(login_req)
    # print login_response.read()
    HtmlFile = os.path.abspath('../temp/userhome.html')
    fout=open(HtmlFile,"w")
    fout.write(login_response.read())
    fout.close()
    webbrowser.open(HtmlFile)
if __name__=='__main__':
    login()