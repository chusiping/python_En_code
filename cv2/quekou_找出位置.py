import aircv as ac
import cv2

image_raw = ac.imread('./temp/v2.jpg') 
image_obj = ac.imread('./temp/qk2.jpg') 

result = ac.find_template(image_raw,image_obj,0.4,True)
print(result)

zuobiao = result["rectangle"]
xmin = zuobiao[0][0]
ymin = zuobiao[0][1]
xmax = zuobiao[2][0]
ymax = zuobiao[3][1]

# 在原始图片上绘制相似的区域
import cv2
image = cv2.imread('./temp/v2.jpg')
cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255), 1)
cv2.imwrite('./temp/v2f.jpg', image)