1. excel_to_config.py
    excel_to_config.py 读取排班表 config.xlsx 生成 task.json 
    异常判断：配置里的excle文件实际不存在目录下，或名称错误，则cmd里提示，防止出异常
    2026-3-5 16:25
        1.config.xlsx 放到config文件夹
        2.指定 config.文件生成
            py excel_to_config.py config/config.xlsx 
        3.增加页面操作 http://localhost:5000/exportjson

2. task.py      排班改成绝对日期，不进行循环
    task.py 读取 config/tasks.json ，等待配置的时间到了，进行多任务发送
    python task.py --send
    逻辑：读取配置到数组，每隔5秒对比数组里的时间。
          系统时间晚于配置里指定的时间，任务加入线程数组。

    2026-3-6 17:59 
        1. 改为动态参数读取json
            python task.py --config config/config.json --no-send
3. 本地测试
    python main_v2.py --excel "excle/科韵路停车场_截断数据.xlsx" --phone 13301110130 --server-ip 14.23.86.188 --server-port 6608 --no-send

4. 以waitress服务启动 服务器ip 172.18.1.197 ，start.bat 不能有中文

5. 测试服务器ip 172.18.2.44（容易搞错）
   2026-3-10 12:2 修改ip操作记录
   替换文件  AFB157-洒水车路线.xlsx  ，配置文件ip变了，修改config文件，再上传，重新生成json     
    停止进程，重新运行一次任务即可


测试转正式需要调整的：
    1. 间隔秒数 _miao = miao
    2. 发送的条数，测试一般是3条5条