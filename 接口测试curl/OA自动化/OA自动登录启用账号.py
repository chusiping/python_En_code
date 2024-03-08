import sys
sys.path.append("./module")
import 常用类库 
import requests
import json
from PIL import Image
from io import BytesIO
session=requests.Session()




url = 'http://172.18.197.10:9099/api/hrm/systeminfo/save'


def send_curl_request():

    login_url = 'http://172.18.197.10:9099/api/hrm/login/checkLogin'  #
    session = requests.Session()
    login_data = {
        "islanguid": "7",
        "loginid": "sysadmin",
        "userpassword": "Qy.test2973",
        "dynamicPassword": "",
        "tokenAuthKey": "",
        "validatecode": "",
        "validateCodeKey": "",
        "logintype": "1",
        "messages": "",
        "isie": "false",
        "appid": "",
        "service": "",
        "isRememberPassword": "false"
    }

    response = session.post(login_url, data=login_data)
    decoded_data = response.content.decode('unicode-escape').encode('latin1').decode('utf8')
    json_data = json.loads(decoded_data)
    print(decoded_data)


    # 检查登录是否成功
    if response.status_code == 200:
        for i in range(1):
                url_ = 'http://172.18.197.10:9099/weaver/weaver.file.MakeValidateCode?isView=1&validatetype=0&validatenum=4&seriesnum_=1709689420493'
                user_input = 常用类库.显示在线验证码图_session方式(session,url_)
                payload={'id': '110954','needauto': '0','enableDate': '2024-03-06','enableUsbType': '0','loginid': '00191514','passwordlock': '0','password': 'qwertyuiop','password1': 'qwertyuiop','clAuthtype': '','usbstate': '0','tokenKey': '','serial': '','startUsing': '','seclevel': '60','useSecondaryPwd': '0','validatecode': user_input }
                print(payload)
                response = session.post(url, data=payload)
                decoded_data = response.content.decode('unicode-escape').encode('latin1').decode('utf8')
                json_data = json.loads(decoded_data)
                print(json_data)

                               
    else:
        print('登录失败:', response.status_code)




  

if __name__ == "__main__":
    send_curl_request()





# 问题描述：普通request方式访问验证码之后再提交数据验证码已经刷新所以总是错误
# 解决方案参考：Python模拟登陆古诗文网手动输入验证码显示验证码错误 https://blog.csdn.net/qq_46302926/article/details/124285290

#  未完成部分
#  数据变数组输入