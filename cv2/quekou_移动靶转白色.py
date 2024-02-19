import cv2  

ksize = (5, 5)
sigmaX = 0
def get_gaussian_blur_image(image):
    return cv2.GaussianBlur(image, ksize, sigmaX)

def get_canny_image(image):
    return cv2.Canny(image, threshold1, threshold2)

def get_contours(image):
    contours, _ = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    return contours

threshold1 = 100 #可调
threshold2 = 550 #可调
pic_path = './temp/'
picName = 'qk'
pic_scr = pic_path +  picName + '.jpg'
pic_gauss =  pic_path + picName + '_gauss.jpg'
pic_canny =  pic_path + picName + '_canny.jpg'
pic_BINARY =  pic_path + picName + '_BINARY.jpg'


src = cv2.imread(pic_scr)# BGR 图像转灰度
gray_img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)# 二值图像处理
r, b = cv2.threshold(gray_img, 250, 255, cv2.THRESH_BINARY)# 显示图像
cv2.imwrite(pic_BINARY, b) # 保存在本地

image_raw = cv2.imread(pic_BINARY) 
image_height, image_width, _ = image_raw.shape
image_gaussian_blur = get_gaussian_blur_image(image_raw)
cv2.imwrite(pic_gauss, image_gaussian_blur )  
image_canny = get_canny_image(image_gaussian_blur)
cv2.imwrite(pic_canny, image_canny )  
contours = get_contours(image_canny) #轮廓信息

print(contours)



# cv2.imshow("1", src)
# cv2.imshow("2", gray_img)
# cv2.imshow("3", b)# 等待显示
# cv2.waitKey(0)
# cv2.destroyAllWindows()