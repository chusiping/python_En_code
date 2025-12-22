#coding=utf-8 方法库，类库集合
import requests,re,os,urllib2
from bs4 import BeautifulSoup
#---- 返回html里的例如div带port属性的集合 关键字：find_all
def GetHtmlTag(html_doc, target_txt, attName):
    soup = BeautifulSoup(html_doc, 'lxml')
    trs = soup.find_all(name=target_txt,attrs={"class":re.compile(r""+ attName +"(\s\w+)?")})
    return trs
#---- Soup过滤html里的Ip
def SoupFindIp(html_doc, idx, ips):
    soup = BeautifulSoup(html_doc, 'lxml')
    try:
        trs = soup.find('table').find_all('tr')
    except:
        print  "soup.find('table') failed !"
        return
    for tr in trs[1:]:
        tds = tr.find_all('td')
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        protocol = tds[3].text.strip()
        if protocol == 'HTTP' or protocol == 'HTTPS':
            # print '%s. %s=%s:%s' % (idx[0], protocol, ip, port)
            ips.append(ip + ':' + port)
            idx[0] = idx[0] + 1
#---- 页面选取定位提取ip 关键字：soup.parent
def GetProxyIpFromTag(html_doc,idx, ips):
    soup = BeautifulSoup(html_doc, 'lxml')
    target_txt = "li"; attName = "port"
    try:
        trs = soup.find_all(name=target_txt, attrs={"class": re.compile(r"" + attName + "(\s\w+)?")})
    except:
        print "li.parent.find failed !"
        return
    for li in trs:
        ip =li.parent.find_previous_sibling().get_text()
        http= li.parent.find_next_sibling().find_next_sibling().get_text()
        port = li.get_text()
        if "http" or "https" in http :
            ips.append(ip+":"+port)
            idx[0] = idx[0] + 1
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
#----  访问网页返回html 关键字：UrlOpen
def Urlopen(_url2):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    req = urllib2.Request(_url2, headers=headers)
    html_doc = urllib2.urlopen(req).read()
    return html_doc
#---- 读取txt文件的每一行，返回集合 open
def OpenReadTxt(TxtFilePath):
    ProxySiteList = os.path.abspath(TxtFilePath)
    if not os.path.exists(ProxySiteList):
        print TxtFilePath + ' - ERROR !'
        exit()
    arr_line=[]
    file = open(ProxySiteList)
    for line in file:
        arr_line.append(line.replace("\n", ""))
    return arr_line
#---- 指定格式txt里所有url的集合
def UrlsFromTxt(TxtFilePath):
    arr_lines = OpenReadTxt(TxtFilePath)
    arr_urls = []
    for urlstr in arr_lines:
        if urlstr[0] == '#':
            continue
        _url = urlstr.split(',')[1]
        _pageCount = int(urlstr.split(',')[0])
        for page in range(1, _pageCount + 1):
            _url2 = _url + str(page)
            if _pageCount == 1:
                _url2 = _url
            arr_urls.append(_url2)
    return arr_urls
if __name__ == '__main__':
    # rt1 = GetHtmlTag('<li class="port GEZEE">101</li><li class="port GEZEE">102</li>', 'li', 'port')
    # rt2 = GetProxyIpFromTag(rt1)
    # rt3 = RequestsGet('http://www.data5u.com/free/gngn/index.shtml')
    # rt4 = RequestsGetByProxy("http://www.winshang.com/index.html",{"http": "http://221.7.255.167:8080"})
    # rt5 = OpenReadTxt('../cc/ProxySiteList.txt')
    rt6 = UrlsFromTxt('../cc/ProxySiteList.txt')
    print rt6