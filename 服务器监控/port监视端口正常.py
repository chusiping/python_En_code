import socket
import time
from datetime import datetime
import json
import requests
import sys

def send_alert_message(obj):
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a6089c2e-3a3f-404a-bbd7-61e9d0d838ce"
    content = "端口访问错误"
    current_time = datetime.now()
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": "<font color=\"warning\">服务器报警</font>，请相关同事注意\n >对象:<font color=\"comment\"> " + obj + " </font>\n >内容:<font color=\"comment\"> " + content + "</font>\n >时间:<font color=\"comment\"> " + current_time.strftime("%Y-%m-%d %H:%M:%S") + "</font>"
        }
    }    
    response = requests.post(url, headers={ "Content-Type": "application/json"}, data=json.dumps(payload))
    
    # if response.status_code == 200:
    #     print("消息发送成功")
    # else:
    #     print(f"消息发送失败，状态码: {response.status_code}")

# sys.exit()

def check_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  
            s.connect((ip, port))
    except socket.error:
        send_alert_message(f"{ip} - {port} is closed")
        print(f"Port {port} is closed on {ip}")

def p_time():
    current_time = datetime.now()
    print("ready to touch port ...:", current_time.strftime("%Y-%m-%d %H:%M:%S"))


def start():
    while True:
        p_time()
        with open('data4.txt', 'r') as file:
            lines = file.readlines()
        for line in lines:
            ip, port = line.strip().split()
            port = int(port)
            check_port(ip, port)
        print("Waiting for 5 minutes will check again ...\n")
        time.sleep(300)  


start()


