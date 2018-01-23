#coding=utf-8
import urllib2,os,re,time
targetDir = "../temp/spader_downed/"
if not os.path.exists(targetDir):
    os.makedirs(targetDir)
def saveFile(data):
    save_path = "../temp/spader_downed/url_all.txt"
    f_obj = open(save_path,'w') # wb 表示打开方式
    f_obj.write(data)
    f_obj.close()

def destFile(path):
    if not os.path.isdir(targetDir):
        os.mkdir(targetDir)
    pos = path.rindex('/')
    t = os.path.join(targetDir, path[pos+1:])
    return t
if __name__ == "__main__":  #程序运行入口
    weburl = "http://www.winshang.com/"
    webheaders = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib2.Request(weburl, headers=webheaders)
    html_doc = urllib2.urlopen(req).read()
    print('star for download......')
    x = 1
    allurl=''



    for link, t in set(re.findall(r'(http:[^\s]*?(jpg|png|gif))', str(html_doc))):  #正则表达式查找所有的图片
        print(str(x) + ':' + link)
        allurl = allurl+ link + '\n';
        try:
            imgName = time.strftime('%Y_%m%d_%H%M%S_',time.localtime(time.time()))+ str(x)+ os.path.basename(link)
            request = urllib2.Request(link, None, webheaders)
            response = urllib2.urlopen(request)
            f = open(targetDir+imgName, 'wb')
            f.write(response.read())
            f.close()
        except:
            print('失败') #异常抛出
        x = x+1
    saveFile(allurl)