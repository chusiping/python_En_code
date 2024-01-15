
import cryptography
import requests
import json
import pymysql
import time
url = 'https://testqyhw.gzqiaoyin.com/api/project/patrolPlan?n=1705039338'
       

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    "Content-Type": "application/json",
    "Authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpblR5cGUiOiJsb2dpbiIsImxvZ2luSWQiOiIwMGIwZDM0ZC1hNWQ2LTQzZjctYTdkNC1jOGQ1ZmJjdjNmN28iLCJyblN0ciI6IkZFOFVIRkdETFlPTXpZYklqVWh3dndLVWVURjRxYnF0IiwidXNlcl9pZCI6IjAwYjBkMzRkLWE1ZDYtNDNmNy1hN2Q0LWM4ZDVmYmN2M2Y3byIsInVzZXJfbmFtZSI6ImFkbWluIiwic2luZ2xlTG9naW4iOjIsImV4cCI6MTcwNTA5MzI1MjQ5MiwidG9rZW4iOiJsb2dpbl90b2tlbl81MTU0OTE5MTc0MzAwNDkyMjEifQ.0SteWmNW0K7e2d6561CMLZIbtTCQRyunwmpphw_maJY"
}



def get_data_from_db():
    # 创建连接参数
    db_config = {
        'host': '172.18.197.7',
        'port': 3306,
        'user': 'zhhw',
        'password': 'zhHW!@#$1234',
        'database': 'qyzhhw_project',
        'charset': 'utf8mb4'
    }
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            query = "SELECT id, area FROM `patrol_area`  limit 3 "  #  SQL 查询语句
            cursor.execute(query)

            for row in cursor.fetchall():
                id = row[0]
                area = row[1]

                send_curl_request(id, area)  # 调用发送请求的函数，并传递参数

    finally:
        connection.close()
def send_curl_request(id,area):
    for i in range(0):
        data={
    "projectId": "13007",
    "patrolAreaId": id,
    "area": area,
    "organizeId": "1001A11000000000HXRJ",
    "enable": 1,
    "patrolUserId": "474253381029261317",
    "patrolUserName": "叶月梅",
    "endTime": "09:31:53"
}
        json_data = json.dumps(data)
        response = requests.post(url, json=json_data, headers=headers)
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


def my_act():
    array = [
        {"id": 474156575972847625, "name": "a"},
        {"id": 474125605152419847, "name": "dd"},
        {"id": 474125608033906698, "name": "kk"}
    ]

    for obj in array:
        obj_id = obj["id"]
        obj_name = obj["name"]
        print(f"ID: , Name: {obj_name}")


        data={
                "projectId":"12967",
                "projectName":"从化街口街环卫一体化",
                "patrolAreaId":"510091489544595333",
                "area":"测试区域2023-12-28",
                "organizeId":"1001A110000000003HD7",
                "enable":1,"enableDesc":"启用",
                "patrolUserId":obj_id,
                "patrolUserName":obj_name,
                "endTime":"14:20:04",
                "type":1
            }
                    
        json_data = json.dumps(data)
        # print(data)
        response = requests.post(url, json=data, headers=headers,verify=True)
        time.sleep(0.5)
        response_data = response.json()
        print(response_data)
            

if __name__ == "__main__":
    # 执行从数据库获取数据并发送请求的操作
    my_act()