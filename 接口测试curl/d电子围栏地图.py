import requests
import json


url = 'https://testqyhw.gzqiaoyin.com/api/project/project/map/rail?n=1704185608'

headers = {
    "Content-Type": "application/json",
    "Authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpblR5cGUiOiJsb2dpbiIsImxvZ2luSWQiOiI0NzQyMTIyMjg4MjUyODA1MTciLCJyblN0ciI6IklweFg0S1BqUVBNUGRjTGVxaThWVzdzaWxnY20xR0wxIiwidXNlcl9pZCI6IjQ3NDIxMjIyODgyNTI4MDUxNyIsInVzZXJfbmFtZSI6IjE4Njg4MzY2NDk2Iiwic2luZ2xlTG9naW4iOjIsImV4cCI6MTcwNDIzNDgwNzgwNywidG9rZW4iOiJsb2dpbl90b2tlbl81MTE4OTEzMzk3MjI0MTA0MzcifQ.hrTT2czg9TNaRlYhl5V2Mo7ygs5s6Exrv0AsAlJLzTg"
}


for i in range(3):
    data={"organizeId":"1001A11000000000HXRJ","mapName":f"wg123{i}","workArea":"0.0042","remark":"www","project":"null","keyword":"null","organizeName":"null","array":[{"lng":113.281143,"lat":23.126298,"orderNum":"1"},{"lng":113.280274,"lat":23.125681,"orderNum":"2"},{"lng":113.281159,"lat":23.125459,"orderNum":"3"},{"lng":113.281138,"lat":23.126283,"orderNum":"4"}],"sliceOrganizeId":"495155132296639045"}
    json_data = json.dumps(data)
    response = requests.post(url, data=json_data, headers=headers)
    response_data = response.json()
    print(response_data)

response_data = response.json()
print(response_data)