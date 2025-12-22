from pywinauto import Application


app = Application(backend='uia').start('D:\Program Files (x86)\Tencent\WeChat\WeChat.exe')
# app = Application(backend='uia').connect(path = r"D:\Program Files (x86)\Tencent\WeChat\WeChat.exe")

# 连接到浏览器进程
browser = app[u'ApplicationFrameWindow']

# 在浏览器中执行操作，例如点击按钮、输入文本等
browser.button1.click()
browser.edit1.type_keys("Hello, World!")

# 关闭浏览器
app.kill()





# import time
# from pywinauto import Application
# from pywinauto.keyboard import send_keys

# app = Application(backend='win32').start('notepad.exe')
# dlg = app.window(class_name='Notepad')

# dlg.menu_select('帮助->关于记事本')
# dlg2 = app["关于“记事本”"]
# time.sleep(1)

# btn_ok = dlg2['确定']
# btn_ok.click()