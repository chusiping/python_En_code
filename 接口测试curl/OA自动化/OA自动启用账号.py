import requests
import json


url = 'http://172.18.197.10:9099/api/hrm/systeminfo/save'

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "ecology_JSessionid=aaadj4X1UH9Ofhmpj-43y; JSESSIONID=aaadj4X1UH9Ofhmpj-43y; languageidweaver=7; loginuuids=1; __randcode__=19a955f3-afaf-441c-a645-ac2d93f4ec62; loginidweaver=sysadmin"
}

def send_curl_request():
    for i in range(1):
        payload={'id': '110954','needauto': '0','enableDate': '2024-03-06','enableUsbType': '0','loginid': '00191514','passwordlock': '0','password': 'qwertyuiop','password1': 'qwertyuiop','clAuthtype': '','usbstate': '0','tokenKey': '','serial': '','startUsing': '','seclevel': '60','useSecondaryPwd': '0','validatecode': '0969`'}
        response = requests.post(url, data=payload, headers=headers)
        decoded_data = response.content.decode('unicode-escape').encode('latin1').decode('utf8')
        json_data = json.loads(decoded_data)
        print(json_data)



if __name__ == "__main__":
    send_curl_request()

