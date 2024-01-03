import json
import subprocess

url="https://api.virapi.com/vir_gitee4b20e17b46226/demo"
url="https://api.virapi.com/vir_gitee4b20e17b46226/test"
app_token = "$2a$10$7UGVE5qu32RoFfa66kJArepiC5eto1hbLhQyUvLVc0ZNNwfqHoaOa"

def send_curl_request():
    data={"id":1001,"content": "评论内容", "imgs": "空"} 
    json_data = json.dumps(data)
    command = f'curl -X POST -H "Content-Type: application/json"  -H "app-token: {app_token}"  {url}'
    # command = f'curl -X POST -H "Content-Type: application/json" -d \'{json_data}\'  -H "app-token: {app_token}"  {url}'
    subprocess.run(command, shell=True)
    print("请求完成！")



url="https://api.virapi.com/vir_gitee4b20e17b46226/demo/comment"
def main():
    for i in range(1, 11):
        data={"id":i,"content": f"评论内容_ {i}", "imgs": f"空 {i}"} 
        # print(data)
        json_data = json.dumps(data)
        command = f'curl -X POST -H "Content-Type: application/json" -d \'{json_data}\' -H "app-token: {app_token}" {url}'
        # print(command)
        subprocess.run(command, shell=True)
    print("提交完成！")

if __name__ == "__main__":
    send_curl_request()
# str.format()