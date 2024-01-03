import requests
import json


url = 'https://testqyhw.gzqiaoyin.com/api/project/project/map/rail?n=1704247533'

headers = {
    "Content-Type": "application/json",
    "Authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpblR5cGUiOiJsb2dpbiIsImxvZ2luSWQiOiI0NzQyMTIyMjg4MjUyODA1MTciLCJyblN0ciI6IlQ2OEI5T2xvTlBhN2ZzeWE0ckIweDhsRmNsODFnMkJzIiwidXNlcl9pZCI6IjQ3NDIxMjIyODgyNTI4MDUxNyIsInVzZXJfbmFtZSI6IjE4Njg4MzY2NDk2Iiwic2luZ2xlTG9naW4iOjIsImV4cCI6MTcwNDMwMTQ1NTkyMywidG9rZW4iOiJsb2dpbl90b2tlbl81MTIxNzA4ODE5MTc3MDA1NDkifQ.VYxczBKe3sne4Eu9hHD4WEnU6B7TNimCrSkbmN7BbME"
}

def send_curl_request():



    for i in range(50):
        data={"organizeId":"1001A11000000000HXRJ","mapName":f"dituname_{i}","workArea":"0.0042","remark":"www","project":"null","keyword":"null","organizeName":"null","array":[{"lng":113.281143,"lat":23.126298,"orderNum":"1"},{"lng":113.280274,"lat":23.125681,"orderNum":"2"},{"lng":113.281159,"lat":23.125459,"orderNum":"3"},{"lng":113.281138,"lat":23.126283,"orderNum":"4"}],"sliceOrganizeId":"495155132296639045"}
        json_data = json.dumps(data)
        response = requests.post(url, data=json_data, headers=headers)
        response_data = response.json()
        print(response_data)

    response_data = response.json()
    print(response_data)

def get_list():

    url = 'https://testqyhw.gzqiaoyin.com/api/project/project/map/rail?n=1704251114'
    data={"currentPage":"1","pageSize":"20","organizeId":"1001A11000000000HXRJ","mapName":"null"}
    json_data = json.dumps(data)
    response = requests.post(url, data=json_data, headers=headers)


    response_data = response.json()
    print(response_data) 

if __name__ == "__main__":
    send_curl_request()