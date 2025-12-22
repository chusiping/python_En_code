import aircv as ac
from PIL import Image
import cv2


class CompareImage():
    # 可以通过confidencevalue来调节相似程度的阈值，小于阈值不相似
    def matchImg(self, imgsrc, imgobj, phone_x, phone_y, confidencevalue=0):  # imgsrc=原始图像，imgobj=待查找的图片
        imsrc = ac.imread(imgsrc)
        imobj = ac.imread(imgobj)
        match_result = ac.find_template(imsrc, imobj, confidencevalue)
        print(match_result)
        if match_result is not None:
            match_result['shape'] = (imsrc.shape[1], imsrc.shape[0])  # 0为高，1为宽
            x, y = match_result['result']  # 标准图中小图位置x,y
            shape_x, shape_y = tuple(map(int, match_result['shape']))  # 标准图中x,y
            position_x, position_y = int(phone_x * (x / shape_x)), int(phone_y * (y / shape_y))
        else:
            return None,None,None,None
        # print(match_result)
        # return match_result
        return position_x, position_y, str(match_result['confidence'])[:4], match_result

    def fixed_size(self, width, height, infile, outfile):
        """按照固定尺寸处理图片"""
        im = Image.open(infile)
        out = im.resize((width, height), Image.ANTIALIAS)
        out.save(outfile)

    def get_picture_size(self, imgsrc):
        '''获取图片长，宽'''
        imsrc = ac.imread(imgsrc)
        y, x, z = imsrc.shape
        return x, y

result = CompareImage().matchImg("quekou_bg.jpg","test_ok.jpg",10,10)
zuobiao = result[3]["rectangle"]
xmin = zuobiao[0][0]
ymin = zuobiao[0][1]
xmax = zuobiao[2][0]
ymax = zuobiao[3][1]

# 在原始图片上绘制相似的区域
import cv2
image = cv2.imread('quekou_bg.jpg')
cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
cv2.imwrite('_result.jpg', image)

