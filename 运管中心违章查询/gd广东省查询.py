import requests
import json


ve="粤A29BN9"

url='https://gd.122.gov.cn/user/m/userinfo/vehs'

headers = {
    "Content-Type": "application/json",
    "cookie": "JSESSIONID-L=3a9933bc-8a8c-4fe1-b64f-0a3a663c67e1; accessToken=iQ61P0glL+Q87gzdSTc8ePC6EcY79l0K8cXw7FGsAMk3pA25VeTL3c1/wZQoE1s8Z+cX5UZBK5nGjlI+HcrnIKNrsh1HB3a7HtJ3j4eFnUwoDrzoPqEZ5G6Fg+AiIlkxY3abDDbTJkKfbFdyIIqLNATs/hv6N8vGsY4nrzCZb8lDjm3FhpntSPL84HbkV1U4; JSESSIONID=0F0495213C93F3C4BCBB3921BFD50E5C; c_yhlx_=2; tmri_csfr_token=408F8C451CD5F2526AFBBC0A2CDC1190"
}

def send_curl_request():
    # data={"startDate":"20210101","endDate":"20211001","hpzl":"02","hphm":"粤A29BN9","page":"1","type":"0"}
    data={"page":1,"size":10,"status":"","hpzl":"02","hphm":""}
    json_data = json.dumps(data)
    response = requests.post(url, data=json_data, headers=headers)
    print(response)

    # response_data = response.json()
    # print(response_data)



if __name__ == "__main__":
    send_curl_request()