#coding=utf-8  测试通过：识别图像中的猫   2017-12-28

from keras.applications.mobilenet import MobileNet
from keras.preprocessing import image
from keras.applications.mobilenet import preprocess_input, decode_predictions
import numpy as np
import sys

model = MobileNet(weights='imagenet')

img_path = sys.argv[1]
img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

preds = model.predict(x)
print('Predicted:', decode_predictions(preds, top=3)[0])

#引用出处：https://zhuanlan.zhihu.com/p/29195626
#测试命令：(root) E:\python_En_code\python35>python pass_py\Pass_IdentCat.py E:\python_En_code\python35\img\cat.jpg
