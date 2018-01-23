#coding=utf-8 测试通过：常用命令
import os
import sys,time
from urllib2 import Request, urlopen, URLError, HTTPError

print '1. '+ str(os.path.exists('../ip.txt'))  #文件存在否
print '2. '+ str(os.path.abspath('../ip.txt')) #文件路径
print '3. 参数个数为:', len(sys.argv), '个参数。' #命令参数个数
print '   参数列表:', str(sys.argv) # 命令参数数组列表
response = urlopen(Request('http://t.cn/zQb28uh'))
print '4. http://t.cn/zQb28uh is ' + response.geturl()
print '5. '+ time.strftime('%Y_%m%d_%H%M%S_',time.localtime(time.time()))
print '6. ' + os.path.basename('http://www.sharejs.com/images/logo.gif')


if len(sys.argv)>1:
    print str(sys.argv[1])
# os.remove('../temp/ip.txt')
if not os.path.exists('../temp/'):
    os.makedirs('../temp/')
