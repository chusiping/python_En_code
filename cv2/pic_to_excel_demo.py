#!/usr/bin/python
#-*- coding: utf-8 -*-
import cv2

# 方法 一
# img = cv2.imread('s1.jpg', 1)
# img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #把彩色图片变为灰色图片
# cv2.imwrite('s1_add1.jpg', img2)

# 方法 二
raw = cv2.imread('s2.jpg', 1)
# 1 彩色图片变为灰色图片
gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY) 
# 2 图片二值化   
binary  = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)

# 3 识别出横线，竖线 在此之后，如果图像不够清晰或者有小像素点，可以使用腐蚀，膨胀等操作让图片更清晰一点
rows, cols = binary.shape
scale = 40
# 自适应获取核值
# 4 识别横线:
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
eroded = cv2.erode(binary, kernel, iterations=1)
dilated_col = cv2.dilate(eroded, kernel, iterations=1)
# cv2.imshow("excel_horizontal_line", dilated_col)


# 5 识别竖线：
scale = 20
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
eroded = cv2.erode(binary, kernel, iterations=1)
dilated_row = cv2.dilate(eroded, kernel, iterations=1)
# cv2.imshow("excel_vertical_line：", dilated_row)

# 6 将识别出来的横竖线合起来
bitwise_and = cv2.bitwise_and(dilated_col, dilated_row)
# cv2.imshow("excel_bitwise_and", bitwise_and)

# 7 标识表格轮廓
merge = cv2.add(dilated_col, dilated_row)
# cv2.imshow("entire_excel_contour：", merge)

# 8 两张图片进行减法运算，去掉表格框线
merge2 = cv2.subtract(binary, merge)
# cv2.imshow("binary_sub_excel_rect", merge2)
new_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
erode_image = cv2.morphologyEx(merge2, cv2.MORPH_OPEN, new_kernel)
merge3 = cv2.add(erode_image, bitwise_and)

# 将焦点标识取出来
ys, xs = np.where(bitwise_and > 0)

# 横纵坐标数组
y_point_arr = []
x_point_arr = []
# 通过排序，排除掉相近的像素点，只取相近值的最后一点
# 这个10就是两个像素点的距离，不是固定的，根据不同的图片会有调整，基本上为单元格表格的高度（y坐标跳变）和长度（x坐标跳变）
i = 0
sort_x_point = np.sort(xs)
for i in range(len(sort_x_point) - 1):
    if sort_x_point[i + 1] - sort_x_point[i] > 10:
        x_point_arr.append(sort_x_point[i])
    i = i + 1
# 要将最后一个点加入
x_point_arr.append(sort_x_point[i])

i = 0
sort_y_point = np.sort(ys)
# print(np.sort(ys))
for i in range(len(sort_y_point) - 1):
    if (sort_y_point[i + 1] - sort_y_point[i] > 10):
        y_point_arr.append(sort_y_point[i])
    i = i + 1
y_point_arr.append(sort_y_point[i])

data = [[] for i in range(len(y_point_arr))]
for i in range(len(y_point_arr) - 1):
    for j in range(len(x_point_arr) - 1):
        # 在分割时，第一个参数为y坐标，第二个参数为x坐标
        cell = src[y_point_arr[i]:y_point_arr[i + 1], x_point_arr[j]:x_point_arr[j + 1]]
        cv2.imshow("sub_pic" + str(i) + str(j), cell)

        # 读取文字，此为默认英文
        # pytesseract.pytesseract.tesseract_cmd = 'E:/Tesseract-OCR/tesseract.exe'
        text1 = pytesseract.image_to_string(cell, lang="chi_sim+eng")

        # 去除特殊字符
        text1 = re.findall(r'[^\*"/:?\\|<>″′‖ 〈\n]', text1, re.S)
        text1 = "".join(text1)
        print('单元格图片信息：' + text1)
        data[i].append(text1)
        j = j + 1
    i = i + 1



cv2.imwrite('s2_1.jpg', binary )        #二值化
cv2.imwrite('s2_2.jpg', dilated_col )   #横线
cv2.imwrite('s2_3.jpg', dilated_row )   #竖线
cv2.imwrite('s2_4.jpg', bitwise_and )   #横竖线交汇点
cv2.imwrite('s2_5.jpg', merge )         #轮廓
cv2.imwrite('s2_6.jpg', merge2 )        #去掉表格框线
cv2.imwrite('s2_7.jpg', merge3 )  
