import cv2

GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
GAUSSIAN_BLUR_SIGMA_X = 0
CANNY_THRESHOLD1 = 250
CANNY_THRESHOLD2 = 380

def get_gaussian_blur_image(image):
    return cv2.GaussianBlur(image, GAUSSIAN_BLUR_KERNEL_SIZE, GAUSSIAN_BLUR_SIGMA_X)

def get_canny_image(image):
    return cv2.Canny(image, CANNY_THRESHOLD1, CANNY_THRESHOLD2)

def get_contours(image):
    contours, _ = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    return contours

image_raw = cv2.imread('test.jpg') 
image_height, image_width, _ = image_raw.shape
image_gaussian_blur = get_gaussian_blur_image(image_raw)
cv2.imwrite('test_rt1.jpg', image_gaussian_blur )  
image_canny = get_canny_image(image_gaussian_blur)
cv2.imwrite('test_rt2.jpg', image_canny )  
contours = get_contours(image_canny)
# print(contours)

def get_contour_area_threshold(image_width, image_height):
    contour_area_min = (image_width * 0.15) * (image_height * 0.25) * 0.8
    contour_area_max = (image_width * 0.15) * (image_height * 0.25) * 1.2
    return contour_area_min, contour_area_max

def get_arc_length_threshold(image_width, image_height):
    arc_length_min = ((image_width * 0.15) + (image_height * 0.25)) * 2 * 0.8
    arc_length_max = ((image_width * 0.15) + (image_height * 0.25)) * 2 * 1.2
    return arc_length_min, arc_length_max

def get_offset_threshold(image_width):
    offset_min = 0.2 * image_width
    offset_max = 0.85 * image_width
    return offset_min, offset_max

contour_area_min, contour_area_max = get_contour_area_threshold(image_width, image_height)
arc_length_min, arc_length_max = get_arc_length_threshold(image_width, image_height)
offset_min, offset_max = get_offset_threshold(image_width)
offset = None
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if contour_area_min < cv2.contourArea(contour) < contour_area_max and \
            arc_length_min < cv2.arcLength(contour, True) < arc_length_max and \
            offset_min < x < offset_max:
        cv2.rectangle(image_raw, (x, y), (x + w, y + h), (0, 0, 255), 2)
        offset = x
cv2.imwrite('test_ok.jpg', image_raw)
print('offset', offset)

# 原始图片我们命名为 image_raw 变量，读取图片之后获取其宽高像素信息，接着调用了 get_gaussian_blur_image 方法进行高斯滤波处理，返回结果命名为 image_gaussian_blur，接着将 image_gaussian_blur 传给 get_canny_image 方法进行边缘检测处理，返回结果命名为 image_canny，接着调用 get_contours 方法得到各个边缘的轮廓信息，赋值为 contours 变量。