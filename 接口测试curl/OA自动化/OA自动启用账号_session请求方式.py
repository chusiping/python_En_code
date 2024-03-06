import sys
sys.path.append("./module")
import 常用类库 
import requests
import json
from PIL import Image
from io import BytesIO
session=requests.Session()


# 问题描述：普通request方式访问验证码之后再提交数据验证码已经刷新所以总是错误
# 解决方案参考：Python模拟登陆古诗文网手动输入验证码显示验证码错误 https://blog.csdn.net/qq_46302926/article/details/124285290

url = 'http://172.18.197.10:9099/api/hrm/systeminfo/save'

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "ecology_JSessionid=aaadj4X1UH9Ofhmpj-43y; JSESSIONID=aaadj4X1UH9Ofhmpj-43y; languageidweaver=7; loginuuids=1; loginidweaver=sysadmin; __randcode__=834790dc-61d6-4168-8dab-01a34b155a49"
}

def send_curl_request():
    for i in range(1):
        url_ = 'http://172.18.197.10:9099/weaver/weaver.file.MakeValidateCode?isView=1&validatetype=0&validatenum=4&seriesnum_=1709689420493'
        user_input = 常用类库.显示在线验证码图_session方式(session,url_,headers)
        payload={'id': '110954','needauto': '0','enableDate': '2024-03-06','enableUsbType': '0','loginid': '00191514','passwordlock': '0','password': 'qwertyuiop','password1': 'qwertyuiop','clAuthtype': '','usbstate': '0','tokenKey': '','serial': '','startUsing': '','seclevel': '60','useSecondaryPwd': '0','validatecode':user_input }
        print(payload)
        response = session.post(url, data=payload, headers=headers)
        decoded_data = response.content.decode('unicode-escape').encode('latin1').decode('utf8')
        json_data = json.loads(decoded_data)
        print(json_data)

       
if __name__ == "__main__":
    send_curl_request()



#  未完成部分
#  数据变数组输入