import cv2
# 代码出处 https://cuiqingcai.com/202292.html
ksize = (5, 5)
sigmaX = 0
threshold1 = 100 #可调
threshold2 = 550 #可调
width_per  = 0.0908  # 目标在画中长比例
height_per = 0.331 # 目标在画中宽比例

pic_path = './temp/'
picName = 'v2'
pic_scr = pic_path +  picName + '.jpg'
pic_BINARY = pic_path + picName + '_1.jpg'
pic_gauss =  pic_path + picName + '_2.jpg'
pic_canny =  pic_path + picName + '_3.jpg'
pic_ok =     pic_path + picName + '_4.jpg'

def get_gaussian_blur_image(image):
    return cv2.GaussianBlur(image, ksize, sigmaX)

def get_canny_image(image):
    return cv2.Canny(image, threshold1, threshold2)

def get_contours(image):
    contours, _ = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    return contours

# 第一步 转黑白
src = cv2.imread(pic_scr)# BGR 图像转灰度
gray_img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)# 二值图像处理
r, b = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY)# 显示图像
# r, b = cv2.threshold(gray_img, 224, 255, cv2.THRESH_BINARY)# 显示图像
cv2.imwrite(pic_BINARY, b) # 保存在本地


image_raw = cv2.imread(pic_BINARY) 
image_height, image_width, _ = image_raw.shape
image_gaussian_blur = get_gaussian_blur_image(image_raw)
cv2.imwrite(pic_gauss, image_gaussian_blur )  
image_canny = get_canny_image(image_gaussian_blur)
cv2.imwrite(pic_canny, image_canny )  
contours = get_contours(image_canny) #轮廓信息
# print(contours)





# 定义目标轮廓的下限和上限面积
def get_contour_area_threshold(image_width, image_height):
    contour_area_min = (image_width * width_per) * (image_height * height_per) * 0.8
    contour_area_max = (image_width * width_per) * (image_height * height_per) * 1.2
    return contour_area_min, contour_area_max
# 定义目标轮廓的下限和上限周长
def get_arc_length_threshold(image_width, image_height):
    arc_length_min = ((image_width * width_per) + (image_height * height_per)) * 2 * 0.9
    arc_length_max = ((image_width * width_per) + (image_height * height_per)) * 2 * 1.1
    return arc_length_min, arc_length_max
# 定义目标轮廓左侧的下限和上限偏移量
def get_offset_threshold(image_width):
    offset_min = 0.1 * image_width
    offset_max = 0.9 * image_width
    return offset_min, offset_max

contour_area_min, contour_area_max = get_contour_area_threshold(image_width, image_height)
arc_length_min, arc_length_max = get_arc_length_threshold(image_width, image_height)
offset_min, offset_max = get_offset_threshold(image_width)
offset = None
print('面积最大最小:',contour_area_min,contour_area_max)
print('周长最小最大:',arc_length_min,arc_length_max)
idx = 0
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)  #轮廓的计算
    _area = w * h
    _zhouchang = (w + h) * 2
    if  contour_area_min < _area < contour_area_max or  arc_length_min > _zhouchang >  arc_length_max:
        print('面积:', w , '*' , h, '=' ,w*h,'周长：',(w+h)*2)
        cv2.rectangle(src, (x, y), (x + w, y + h), (0, 255, 255), 2)
    # if contour_area_min < cv2.contourArea(contour) < contour_area_max and arc_length_min < cv2.arcLength(contour, True) < arc_length_max and offset_min < x < offset_max:
    #     cv2.rectangle(image_raw, (x, y), (x + w, y + h), (0, 255, 255), 2)
    #     print(idx,'画框：x:',x ,'y:',y  ,'宽:' ,(x + w) ,'高:' ,  (y + h),'面积:', w , '*' , h, '=' ,w*h)
    # if idx in (9,11)   :
    #     print('画框：',idx,  x , y  , (x + w) ,  (y + h),'面积:', w , '*' , h, '=' ,w*h)
    #     print('周长：',(w+h)*2)
    #     cv2.rectangle(image_raw, (x, y), (x + w, y + h), (0, 255, 255), 2)
        offset = x
    idx=idx+1
cv2.imwrite(pic_ok, src)
print('offset', offset)

# 原始图片我们命名为 image_raw 变量，读取图片之后获取其宽高像素信息，接着调用了 get_gaussian_blur_image 方法进行高斯滤波处理，返回结果命名为 image_gaussian_blur，接着将 image_gaussian_blur 传给 get_canny_image 方法进行边缘检测处理，返回结果命名为 image_canny，接着调用 get_contours 方法得到各个边缘的轮廓信息，赋值为 contours 变量。
# x   	y 
# 986   335 
# 93  	93

# cv2.rectangle(image, start_point, end_point, color, thickness)参数
# image:它是要在其上绘制矩形的图像。
# start_point：它是矩形的起始坐标。坐标表示为两个值的元组，即(X坐标值，Y坐标值)。
# end_point：它是矩形的结束坐标。坐标表示为两个值的元组，即(X坐标值ÿ坐标值)。
# color:它是要绘制的矩形的边界线的颜色。对于BGR，我们通过一个元组。例如：(255，0，0)为蓝色。
# thickness:它是矩形边框线的粗细像素。厚度-1像素将以指定的颜色填充矩形形状。
# 代码出处https://blog.csdn.net/sinat_41104353/article/details/85171185