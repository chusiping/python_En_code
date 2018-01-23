#encoding=utf8 测试通过：完善中
#                        自动下载验证码到本地，人工查看手动输入验证码登陆赣州房管

import urllib2, urllib, cookielib
img_url = 'http://218.64.195.220:8001/account/VerificationCode?0.9076473457215115'
login_url = 'http://218.64.195.220:8001/account/LoginHandlekey?step=0&id=&rownum=ab0.9076473457215115&id2='
data_url ='http://218.64.195.220:8001//Enterprise//CYQYGL.aspx?qylb=1&bid=&fid=759d870a-aff2-416b-b60f-ea31b5a59463&nc=ck&new=1'
username = 'lk091101'
password = '123'

def login():
    CookFile_1 = "../temp/LoginOut.txt";CookFile_2 = "../temp/LoginIn.txt"
    cookie_1 = cookielib.MozillaCookieJar(CookFile_1);cookie_2 = cookielib.MozillaCookieJar(CookFile_2)
    opener =urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_1))
    print ('open img urlsuccess')

    urllib2.install_opener(opener)
    img_req=urllib2.Request(img_url)
    img_response=opener.open(img_req)
    cookie_1.save(ignore_discard=True, ignore_expires=True)
    try:
        out = open('../temp/code.png', 'wb')
        # print img_response.read()
        out.write(img_response.read())
        out.flush()
        out.close()
        print 'get code success'
    except IOError:
        print 'file wrong'
    img_code = raw_input("please input code: ")

    print 'your code is：%s '%img_code
    #login
    LoginData = {
       'username':username,
       'password':password,
       'code':img_code,
       };
    login_req =urllib2.Request(login_url, urllib.urlencode(LoginData));
    login_req.add_header('User-Agent', "Mozilla/5.0 (X11; Ubuntu; Linuxx86_64; rv:31.0) Gecko/20100101 Firefox/31.0");
    login_response=opener.open(login_req)
    print login_response.read()
    cookie_1.save(ignore_discard=True, ignore_expires=True)

if __name__=='__main__':
    login()