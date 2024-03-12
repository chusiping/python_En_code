import socket
import time
from datetime import datetime

def check_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  
            s.connect((ip, port))
            # print(f"Port {port} is open on {ip}")
    except socket.error:
        print(f"Port {port} is closed on {ip}")

def p_time():
    current_time = datetime.now()
    print("ready to touch port ...:", current_time.strftime("%Y-%m-%d %H:%M:%S"))


def heartBeat():
    print('心跳...')

while True:
    p_time()
    heartBeat()
    with open('data4.txt', 'r') as file:
        lines = file.readlines()
    for line in lines:
        ip, port = line.strip().split()
        port = int(port)
        check_port(ip, port)
    print("Waiting for 5 minutes will check again ...\n")
    time.sleep(3)  






