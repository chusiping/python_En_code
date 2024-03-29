import requests
import json
from PIL import Image
from io import BytesIO
import time
session=requests.Session()
host = 'http://172.18.197.10:9099'


def 显示在线验证码图_session方式(Session,_url):
    response = Session.get(url=_url)
    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        image.show()
        user_input = input("请输入验证码：")
        return user_input
    else:
        raise RuntimeError("Failed to fetch image")





def send_curl_request():
    login_url = 'http://172.18.197.10:9099/api/hrm/login/checkLogin'  #
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
                url_ = host + '/weaver/weaver.file.MakeValidateCode?isView=1&validatetype=0&validatenum=4&seriesnum_=1709689420493'
                current_timestamp = str(int(time.time() * 1000))
                url_ = url_.replace('1709689420493', current_timestamp)
                user_input = 显示在线验证码图_session方式(session,url_)
                payload={'id': '110954','needauto': '0','enableDate': '2024-03-06','enableUsbType': '0','loginid': '00191514','passwordlock': '0','password': 'qwertyuiop','password1': 'qwertyuiop','clAuthtype': '','usbstate': '0','tokenKey': '','serial': '','startUsing': '','seclevel': '60','useSecondaryPwd': '0','validatecode': user_input }
                print(payload)
                url = host + '/api/hrm/systeminfo/save'
                response = session.post(url, data=payload)
                decoded_data = response.content.decode('unicode-escape').encode('latin1').decode('utf8')
                json_data = json.loads(decoded_data)
                print(json_data)
               
    else:
        print('登录失败:', response.status_code)

if __name__ == "__main__":
    send_curl_request()
    input("Press Enter to exit")


# 问题描述：普通request方式访问验证码之后再提交数据验证码已经刷新所以总是错误
# 解决方案参考：Python模拟登陆古诗文网手动输入验证码显示验证码错误 https://blog.csdn.net/qq_46302926/article/details/124285290
# 未完成部分
# 数据变数组输入
# Pyinstaller -F OA自动登录启用账号.py