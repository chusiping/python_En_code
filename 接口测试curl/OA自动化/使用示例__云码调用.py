import sys
sys.path.append("./module")
import 云码验证码类
import base64

y = 云码验证码类.YdmVerify()
with open("./img/验证码.jpg", "rb") as image_file:

# 读取图像文件的二进制数据
    base64_image = image_file.read()
    y.common_verify(base64_image,"10110")



#测试通过