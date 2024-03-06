import sys
sys.path.append("./module")
import 常用类库 

url = 'http://172.18.197.10:9099/weaver/weaver.file.MakeValidateCode?isView=1&validatetype=0&validatenum=4&seriesnum_=1709689420493'
rt=常用类库.显示在线验证码图(url)
print(rt)