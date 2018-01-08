# encoding=utf-8
from PIL import Image
from pytesser import *




img = Image.open('img/1.jpg')
img_grey = img.convert('L')

threshold = 140
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)
img_out = img_grey.point(table, '1')

text = image_to_string(img_grey)  # 将图片转成字符串
# print text