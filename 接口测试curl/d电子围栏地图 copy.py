import requests
import json

# 定义接口 URL
url = 'https://testqyhw.gzqiaoyin.com/api/project/project/map/rail?n=1704185608'

# 定义要提交的 JSON 数据
data = {
  "organizeId": "1001A11000000000HXRJ",
  "mapName": "wg113",
  "workArea": "0.0042",
  "remark": "www",
  "project": "null",
  "keyword": "null",
  "organizeName": "null",
  "array": [
    {
      "lng": 113.281143,
      "lat": 23.126298,
      "orderNum": "1"
    },
    {
      "lng": 113.280274,
      "lat": 23.125681,
      "orderNum": "2"
    },
    {
      "lng": 113.281159,
      "lat": 23.125459,
      "orderNum": "3"
    },
    {
      "lng": 113.281138,
      "lat": 23.126283,
      "orderNum": "4"
    }
  ],
  "sliceOrganizeId": "495155132296639045"
}


# 将 JSON 数据转换为字符串
json_data = json.dumps(data)

# 设置请求头，包括 Authorization
headers = {
    "Content-Type": "application/json",
    "Authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpblR5cGUiOiJsb2dpbiIsImxvZ2luSWQiOiI0NzQyMTIyMjg4MjUyODA1MTciLCJyblN0ciI6IklweFg0S1BqUVBNUGRjTGVxaThWVzdzaWxnY20xR0wxIiwidXNlcl9pZCI6IjQ3NDIxMjIyODgyNTI4MDUxNyIsInVzZXJfbmFtZSI6IjE4Njg4MzY2NDk2Iiwic2luZ2xlTG9naW4iOjIsImV4cCI6MTcwNDIzNDgwNzgwNywidG9rZW4iOiJsb2dpbl90b2tlbl81MTE4OTEzMzk3MjI0MTA0MzcifQ.hrTT2czg9TNaRlYhl5V2Mo7ygs5s6Exrv0AsAlJLzTg"
}

# 发起 POST 请求
response = requests.post(url, data=json_data, headers=headers)

# 获取响应数据
response_data = response.json()

# 打印响应数据
print(response_data)