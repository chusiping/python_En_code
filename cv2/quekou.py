import cv2
bg_img = cv2.imread('quekou_bg.jpg') # 背景图片
tp_img = cv2.imread('quekou.jpg') # 缺口图
bg_edge = cv2.Canny(bg_img, 100, 200)
tp_edge = cv2.Canny(tp_img, 100, 200)
bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)

min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

X = max_loc[0] 

th, tw = tp_pic.shape[:2] 
tl = max_loc # 左上角点的坐标
br = (tl[0]+tw,tl[1]+th) # 右下角点的坐标
cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2) # 绘制矩形
cv2.imwrite('test_ok.jpg', bg_img) # 保存在本地

#代码出处https://blog.csdn.net/zhangzeyuaaa/article/details/119508407