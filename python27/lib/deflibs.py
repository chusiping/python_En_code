#coding=utf-8 方法库，类库集合
import requests,re
from bs4 import BeautifulSoup
#---- 返回html里的例如div带port属性的集合 关键字：find_all
def GetHtmlTag(html_doc, target_txt, attName):
    soup = BeautifulSoup(html_doc, 'lxml')
    trs = soup.find_all(name=target_txt,attrs={"class":re.compile(r""+ attName +"(\s\w+)?")})
    return trs
#---- 页面选取定位提取ip 关键字：soup.parent
def GetProxyIpFromTag(soup_txt):
    arr_ip =[]
    for li in soup_txt:
        ip =li.parent.find_previous_sibling().get_text()
        http= li.parent.find_next_sibling().find_next_sibling().get_text()
        port = li.get_text()
        if "http" or "https" in http :
            arr_ip.append(http[0:4] + "://" + ip+":"+port)
    return arr_ip
#---- 访问网页返回类 关键字：requests
def RequestsGet(httpUrl):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    r = requests.get(httpUrl, headers=headers)
    return r
#---- 使用代理访问网页返回类 关键字：requests
def RequestsGetByProxy(httpUrl,Proxy):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    r = requests.get(httpUrl, proxies=Proxy,headers=headers)
    return r


if __name__ == '__main__':
    # rt1 = GetHtmlTag('<li class="port GEZEE">101</li><li class="port GEZEE">102</li>', 'li', 'port')
    # rt2 = GetProxyIpFromTag(rt1)
    # rt3 = RequestsGet('http://www.data5u.com/free/gngn/index.shtml')
    rt4 = RequestsGetByProxy("http://www.winshang.com/index.html",{"http": "http://221.7.255.167:8080"})
    print rt4