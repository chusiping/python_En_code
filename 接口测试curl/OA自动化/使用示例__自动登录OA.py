import requests
import json

def login_and_get_session():
    login_url = 'http://172.18.197.10:9099/api/hrm/login/checkLogin'  # 替换为实际的登录页面 URL
    target_url = 'http://example.com/target_page'  # 替换为实际需要访问的页面 URL
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

login_and_get_session()
