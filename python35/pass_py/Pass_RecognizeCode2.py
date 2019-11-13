from PIL import Image
from pytesseract import *
im = Image.open('1.jpg')
im = im.convert('L')
def initTable(threshold=140):
 table = []
 for i in range(256):
     if i < threshold:
         table.append(0)
     else:
         table.append(1)

 return table
binaryImage = im.point(initTable(), '1')
# binaryImage.show()
print(image_to_string(binaryImage))