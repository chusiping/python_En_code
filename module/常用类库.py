import requests
from PIL import Image
from io import BytesIO
session=requests.Session()

def 显示在线验证码图(_url):
    response = requests.get(_url)
    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        image.show()
        user_input = input("请输入验证码：")
        return user_input
    else:
        raise RuntimeError("Failed to fetch image")

# 用session请求验证码地址输入验证码后才不会报错
def 显示在线验证码图_session方式(Session,_url):
    response = Session.get(url=_url)
    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        image.show()
        user_input = input("请输入验证码：")
        return user_input
    else:
        raise RuntimeError("Failed to fetch image")


