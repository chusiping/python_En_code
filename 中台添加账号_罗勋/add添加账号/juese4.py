import requests
import json

# 从config.json文件中读取配置信息
with open('config.json') as f:
    config = json.load(f)

# 从txt文件中读取员工数据，假设文件名为'employee_data.txt'
with open('employee_data.txt', 'r', encoding='utf-8') as txt_file:
    text_data = txt_file.read().replace('\n', ';').strip()  # 将换行符替换为分号，并去除首尾空格

# 将文本分割为员工记录列表
employee_records = text_data.split("；")

for record in employee_records:
    # 去除多余的空格并按照分隔符拆分记录
    parts = record.strip().split("-")

    if len(parts) >= 4:  # 确保记录包含姓名、工号、部门和职位
        userNo = parts[1].strip()  # 提取工号并去除前后空格
        print(userNo)
        position = parts[3].strip()  # 提取职位并去除前后空格

        group_id_for_position = config['groupIdZN']  # 默认设置为"项目经理"

        # 根据职位判断group_id
        if position == "项目总经理":
            group_id_for_position = config['groupIdXMZJL']
        elif "项目副总经理" in position:
            group_id_for_position = config['groupIdXMFZJL']
        elif "项目储备干部" in position:
            group_id_for_position = config['groupIdCBGB']

        # 对于每个账号执行一次额外的POST请求，使用groupIdJCJS
        default_group_id = config['groupIdJCJS']

        search_params = {
            "tenantId": "1",
            "groupId": "",
            "isSpecifyUserGroups": "undefined",
            "initGroupId": "",
            "groupId": "",
            "fullname": "",  # 如果搜索需要使用姓名，可以在这里赋值 parts[0]
            "userNo": userNo
        }

        search_url = config['searchUrl']
        join_user_url = config['joinUserUrl']
        cookie = config['cookie']
        referer = config['referer']

        response_search = requests.get(search_url, params=search_params)
        response_json = response_search.json()

        if response_json['total'] > 0:
            user_data = response_json['data'][0]
            user_id = user_data['userId']

            # 准备payload数据，并发送根据职位获取的group_id POST请求
            payload_for_position = {
                "userIds": user_id,
                "relTypeId": "1",
                "tenantId": "1",
                "groupId": group_id_for_position
            }

            headers = {
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://eip.gzqiaoyin.com",
                "X-Requested-With": "XMLHttpRequest",
                "Cookie": cookie,
                "Referer": referer
            }

            response2_for_position = requests.post(join_user_url, data=payload_for_position, headers=headers)

            # 检查响应状态码及内容...

            # 准备payload数据，并发送额外的groupIdJCJS POST请求
            payload_for_default = {
                "userIds": user_id,
                "relTypeId": "1",
                "tenantId": "1",
                "groupId": default_group_id
            }

            response2_for_default = requests.post(join_user_url, data=payload_for_default, headers=headers)
            print(response2_for_default.text)

            # 检查响应状态码及内容（与上面类似）
        else:
            print(f"未找到工号为 {userNo} 的用户信息，将跳过所有POST请求")