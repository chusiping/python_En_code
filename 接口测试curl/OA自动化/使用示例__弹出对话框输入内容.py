# 上面说了，Entry是单行文本输入框，如果我们想要输入多行文本该怎么办呢？
from tkinter import *

window = Tk()
window.geometry('500x500')

name_input = Text(window,width='40',height='6')		
name_input.pack()


def print_name():
    print(name_input.get('1.0','1.5'))				    # 可以用get()方法获取Text的文本内容 print(name_input.get('1.0','1.5'))
    												# 其中第一个参数是起始位置，'1.1'就是从第一行第一列后，到第一行第五列后
Button(window,text='请输入数据内容',command=print_name).pack()


def center_window(w, h):
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
center_window(500, 500)



window.mainloop()



