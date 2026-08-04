def parse_bits16(b):
    """
    16bit状态解析
    返回bit列表
    """
    value=int.from_bytes(b,"big")

    result={}

    names=[
        "Catalyst催化转化器",
        "Heated catalyst加热催化器",
        "Evaporative system蒸发系统",
        "Secondary air二次空气",
        "A/C制冷剂",
        "Exhaust Gas Sensor排气传感器",
        "Sensor heater传感器加热",
        "EGR/VVT",
        "Cold start冷启动",
        "Boost pressure增压",
        "DPF",
        "SCR/NOx",
        "NMHC催化器",
        "Misfire失火",
        "Fuel system燃油系统",
        "Comprehensive component综合部件"
    ]

    for i,name in enumerate(names):
        bit=15-i
        result[name]=bool(value&(1<<bit))

    return result

def parse_ascii(b):
    return b.decode(
        "ascii",
        errors="ignore"
    ).replace("\x00","")

def parse_work_status(b, bit_names):
    """
    环卫车工况bit解析 (完全适配 0 和 1 都有含义的复合工况)
    b: 4字节
    bit_names: {bit: 名称字符串 或 {0:文本, 1:文本}}
    """
    value = int.from_bytes(b, "big")
    result = {}
    for bit, config in bit_names.items():
        if bit >= 32:  # 安全防御，防止超出4字节
            continue
        # 核心：检查该位是 1 还是 0
        is_on = bool(value & (1 << bit))
        # 情况 A：如果配置是个字典，说明 0 和 1 都有明确的文本含义
        if isinstance(config, dict):
            # 找到对应状态的名字，比如 BIT6 的 "功能切换"
            key_name = config.get("name", f"BIT{bit}")
            # 根据 0 或 1 取出对应的文字
            result[key_name] = config[1] if is_on else config[0]
        # 情况 B：如果配置只是普通字符串，代表 1 是开启，0 是关闭
        else:
            result[config] = "开" if is_on else "关"
    return result


TRUCK_EXT_CONFIG = {

    # =============================
    # OBD 基础数据
    # =============================

    "60C0":{
        "name":"OBD转速",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"rpm"
    },


    "60D0":{
        "name":"OBD车速",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"km/h"
    },


    "62F0":{
        "name":"OBD剩余油量",
        "len":2,
        "parser":lambda b:{
            "value":(int.from_bytes(b,"big") & 0x7FFF)/10,  #0x7FFF 的完整二进制是：0111 1111 1111 1111（共 16 位，最高位是 0，其余 15 位都是 1）。
            "unit":"L" if int.from_bytes(b,"big")&0x8000 else "%" #0x8000 的二进制是：1000 0000 0000 0000
        }
    },


    "6050":{
        "name":"OBD冷却液温度",
        "len":1,
        "parser":lambda b:b[0]-40,
        "unit":"℃"
    },


    "60F0":{
        "name":"OBD进气温度",
        "len":1,
        "parser":lambda b:b[0]-40,
        "unit":"℃"
    },


    "60B0":{
        "name":"OBD进气压力",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"kPa"
    },


    "50B0":{
        "name":"OBD进气压力(货车)",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"kPa"
    },


    "6330":{
        "name":"OBD大气压力",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"kPa"
    },


    "6460":{
        "name":"OBD环境温度",
        "len":1,
        "parser":lambda b:b[0]-40,
        "unit":"℃"
    },


    "6490":{
        "name":"加速踏板位置",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"%"
    },


    "60A0":{
        "name":"OBD燃油压力",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"kPa"
    },


    "6010":{
        "name":"OBD故障码数量",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"个"
    },


    "5001":{
        "name":"OBD离合器开关",
        "len":1,
        "parser":lambda b:"开" if b[0]==1 else "关"
    },


    "5002":{
        "name":"OBD制动刹车开关",
        "len":1,
        "parser":lambda b:"开" if b[0]==1 else "关"
    },


    "5003":{
        "name":"OBD驻车刹车开关",
        "len":1,
        "parser":lambda b:"开" if b[0]==1 else "关"
    },


    "5004":{
        "name":"OBD节流阀位置",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"%"
    },


    "5005":{
        "name":"发动机燃油流量",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.05,
        "unit":"L/h"
    },


    "5006":{
        "name":"OBD燃油温度",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.03125-273,
        "unit":"℃"
    },


    "5007":{
        "name":"OBD机油温度",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.03125-273,
        "unit":"℃"
    },


    "5008":{
        "name":"发动机润滑油压力",
        "len":1,
        "parser":lambda b:b[0]*4,
        "unit":"kPa"
    },


    "5009":{
        "name":"制动器踏板位置",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"%"
    },


    "500A":{
        "name":"空气流量",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.1,
        "unit":"g/s"
    },


    # =============================
    # 扭矩 SCR
    # =============================


    "5101":{
        "name":"发动机净输出扭矩",
        "len":1,
        "parser":lambda b:b[0]-125,
        "unit":"%"
    },


    "5102":{
        "name":"摩擦扭矩",
        "len":1,
        "parser":lambda b:b[0]-125,
        "unit":"%"
    },


    "5103":{
        "name":"SCR上游NOx",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.05-200,
        "unit":"ppm"
    },


    "5104":{
        "name":"SCR下游NOx",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.05-200,
        "unit":"ppm"
    },


    "5105":{
        "name":"反应剂余量",
        "len":1,
        "parser":lambda b:b[0]*0.4,
        "unit":"%"
    },


    "5106":{
        "name":"进气量",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.05,
        "unit":"Kg/h"
    },


    "5107":{
        "name":"SCR入口温度",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.03125-273,
        "unit":"℃"
    },


    "5108":{
        "name":"SCR出口温度",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.03125-273,
        "unit":"℃"
    },


    "5109":{
        "name":"DPF压差",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.1,
        "unit":"kPa"
    },


    "510A":{
        "name":"发动机扭矩模式",
        "len":1,
        "parser":lambda b:{
            0:"超速失效",
            1:"转速控制",
            2:"扭矩控制",
            3:"转速/扭矩控制",
            9:"正常"
        }.get(b[0],"未知")
    },


    "510B":{
        "name":"油门踏板",
        "len":1,
        "parser":lambda b:b[0]*0.4,
        "unit":"%"
    },


    "510C":{
        "name":"尿素箱温度",
        "len":1,
        "parser":lambda b:b[0]-40,
        "unit":"℃"
    },


    "510D":{
        "name":"实际尿素喷射量",
        "len":4,
        "parser":lambda b:int.from_bytes(b,"big")*0.01,
        "unit":"ml/h"
    },


    "510E":{
        "name":"累计尿素消耗",
        "len":4,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"g"
    },


    "510F":{
        "name":"DPF排气温度",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.03125-273,
        "unit":"℃"
    },


    "5110":{
        "name":"发动机燃油流量",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.05,
        "unit":"L/H"
    },


    "5111":{
        "name":"OBD诊断协议",
        "len":1,
        "parser":lambda b:{
            0:"IOS15765",
            1:"IOS27145",
            2:"SAEJ1939",
            0xFE:"无效"
        }.get(b[0],"未知")
    },


    "5112": {
        "name": "MIL状态",
        "len": 1,
        "parser": lambda b: "无效" if b[0] == 0xFE else ("点亮" if b[0] == 1 else "未点亮"),
        "unit": ""
    },
    "511F":{
        "name":"发动机实时负载",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"%"
    },
    "5113":{
        "name":"诊断支持状态",
        "len":2,
        "parser":parse_bits16
    },
    "5114":{
        "name":"诊断就绪状态",
        "len":2,
        "parser":parse_bits16
    },
    # ================================
    # VIN / 标定
    # =================================
    "5115":{
        "name":"车辆识别码VIN",
        "len":17,
        "parser":parse_ascii
    },
    "5116":{
        "name":"软件标定识别号",
        "len":18,
        "parser":parse_ascii
    },
    "5117":{
        "name":"标定验证码CVN",
        "len":18,
        "parser":parse_ascii
    },
    "5118":{
        "name":"IUPR值",
        "len":36,
        "parser":lambda b:b.hex().upper()
    },
    # =================================
    # 排放相关
    # =================================
    "511A":{
        "name":"光吸收系数",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.01,
        "unit":"m-1"
    },
    "511B":{
        "name":"不透光度",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.1,
        "unit":"%"
    },
    "511C":{
        "name":"颗粒物浓度",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"Mg/m3"
    },
    "5120":{
        "name":"三元催化器上游氧传感器",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"V"
    },
    "5121":{
        "name":"三元催化器下游氧传感器",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"V"
    },
    "5122":{
        "name":"三元催化器温度传感器",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"℃"
    },
    # =================================
    # 农机 / 专用设备
    # =================================
    "5201":{
        "name":"当前粉松压力",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.01,
        "unit":"Mpa"
    },
    "5202":{
        "name":"当前左行走压力",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.01,
        "unit":"Mpa"
    },
    "5203":{
        "name":"当前右行走压力",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.01,
        "unit":"Mpa"
    },
    "5204":{
        "name":"当前粉松转速",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"rpm"
    },
    "5205":{
        "name":"当前燃油液位报警",
        "len":1,
        "parser":lambda b:"报警" if b[0]==1 else "正常"
    },
    "5206":{
        "name":"粉松手柄左右转向",
        "len":1,
        "parser":lambda b:{
            0:"左转",
            1:"右转"
        }.get(b[0],"未知")
    },
    "5207":{
        "name":"挡位状态",
        "len":1,
        "parser":lambda b:{
            0:"空挡",
            1:"前进档",
            2:"后退挡"
        }.get(b[0],"未知")
    },
    "5208":{
        "name":"锁定状态",
        "len":1,
        "parser":lambda b:{
            0:"可行走",
            1:"行走锁定"
        }.get(b[0],"未知")
    },
    "5209":{
        "name":"农机状态",
        "len":1,
        "parser":lambda b:{
            0:"待机",
            1:"工作"
        }.get(b[0],"未知")
    },
    "520A":{
        "name":"粉松发动机总运行时间",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")*0.1,
        "unit":"H"
    },
    "520B":{
        "name":"冷却剂低液位报警",
        "len":1,
        "parser":lambda b:"报警" if b[0]==1 else "正常"
    },
    "520C":{
        "name":"发动机机油低报警",
        "len":1,
        "parser":lambda b:"报警" if b[0]==1 else "正常"
    },
    "520D":{
        "name":"气压报警指示器",
        "len":1,
        "parser":lambda b:"开" if b[0] else "关"
    },
    "520E":{
        "name":"排气制动开关",
        "len":1,
        "parser":lambda b:"开" if b[0] else "关"
    },
    "520F":{
        "name":"发动机参考扭矩",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big")
    },
    "5210":{
        "name":"环卫车副发动机摩擦扭矩",
        "len":1,
        "parser":lambda b:b[0]-125,
        "unit":"%"
    },
    "5211":{
        "name":"环卫车副发动机冷却液温度",
        "len":1,
        "parser":lambda b:b[0]-40,
        "unit":"℃"
    },
    "5212":{
        "name":"环卫车副发动机大气压力",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"kPa"
    },
    "5213":{
        "name":"环卫车副发动机负载",
        "len":1,
        "parser":lambda b:b[0],
        "unit":"%"
    },
    "5214":{
        "name":"环卫车副发动机转速",
        "len":2,
        "parser":lambda b:int.from_bytes(b,"big"),
        "unit":"rpm"
    },
    "5215":{
        "name":"环卫车副发动机扭矩百分比",
        "len":1,
        "parser":lambda b:b[0]-125,
        "unit":"%"
    },
    "5216":{
        "name":"环卫车副发动机扭矩百分比阈值",
        "len":1,
        "parser":lambda b:b[0]-125,
        "unit":"%"
    },
    # ============================================
    # 环卫车工况
    # ============================================
    "5217":{
        "name":"环卫车工况(宇通环卫)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"全扫开",
            1:"全喷",
            2:"喷雾开",
            3:"扫刷低速开",
            4:"扫刷中速开",
            5:"低速降尘开",
            6:"左工作灯开",
            7:"右工作灯开",
        })
    },
    "5218":{
        "name":"环卫车工况(福龙马)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"扫开",
            1:"洗开",
            2:"洗扫开",
            3:"扫盘喷水开",
            4:"左前洒水开",
            5:"右前洒水开",
            6:"左侧冲开",
            7:"右侧冲开",
        })
    },
    "5219":{
        "name":"环卫车工况(中通洗扫车)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"全洗扫作业开",
            1:"左洗扫作业开",
            2:"右洗扫作业开",
            3:"扫盘高速开",
            4:"扫盘中速开",
            5:"扫盘低速开",
            6:"喷淋开",
            7:"左对冲开",
            8:"右对冲开",
        })
    },
    "521A":{
        "name":"环卫车工况(盈峰环境)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"后区作业开",
            1:"满箱提示开",
            2:"锁开提示开",
            3:"填装器升开",
            4:"填装器降开",
            5:"推铲卸料开",
            6:"推铲回位开",
        })
    },
    "521B":{
        "name":"环卫车工况(中联环境)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"全喷水扫作业开",
            1:"左喷水扫作业开",
            2:"右喷水扫作业开",
            3:"扫盘高速开",
            4:"扫盘中速开",
            5:"扫盘低速开",
            6:"全不喷水扫开",
            7:"左不喷水扫开",
            8:"右不喷水扫开",
        })
    },



    "521C":{
        "name":"环卫车工况(普罗科喷水架)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"左角喷喷水开",
            1:"右角喷喷水开",
            2:"喷水架喷水开",
            3:"后喷雾喷水开",
            4:"喷水架左摆开",
            5:"喷水架右摆开",
            6:"喷水架下降开",
            7:"喷水架上升开",
            8:"左喷水架缩开",
            10:"左喷水架伸开",
            11:"右喷水架缩开",
            12:"右喷水架伸开",
        })
    },
    "521D":{
        "name":"环卫车工况(普罗科高压清洗)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"分离器箱分离开",
            1:"前定点清淤开",
            2:"左角喷喷水开",
            3:"右角喷喷水",
            4:"喷水架喷水开",
            5:"后喷雾喷水开",
            6:"喷水架左摆开",
            7:"喷水架右摆开",
            8:"喷水架下降开",
            9:"喷水架展开开",
            10:"警示灯开",
            11:"音乐喇叭开",
            12:"左箭头开",
            13:"右箭头开",
        })
    },
    "521E":{
        "name":"环卫车工况(环卫面板1)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"装载开",
            1:"卸载开",
            2:"抬后兜开",
            3:"放后兜开",
            4:"推灰开",
            5:"收灰开",
            6:"清除开",
            7:"总电源开",
        })
    },
    "521F":{
        "name":"环卫车工况(福龙马清扫车)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"全扫开",
            1:"左扫开",
            2:"右扫开",
            3:"增强压尘",
            4:"扫盘喷水",
            5:"后门开",
            6:"后门关",
            7:"总电源开",
            8:"扫盘喷水",
            9:"后门开",
            10:"后门关",
            11:"料箱倾翻",
            12:"料箱复位",
            13:"警铃",
            14:"工作灯",
            15:"警灯",
        })
    },
    "5220":{
        "name":"环卫车工况(海德路面清洗车)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"喷水作业开",
            1:"单点",
            2:"左摆",
            3:"右摆",
            4:"升作业",
            5:"降作业",
        })
    },
    "5221":{
        "name":"环卫车工况(环卫面板_2)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"急停按钮",
            1:"面板背光灯",
            2:"警示灯",
            3:"手动模式",
            4:"维修模式",
            5:"翻桶",
            6:"报警喇叭",
            7:"卸料准备",
            8:"推铲卸料",
            9:"尾门开锁",
            10:"尾门开启",
            11:"行车准备",
            12:"推铲回位",
            13:"尾门锁止",
            14:"尾门关闭",
        })
    },
    "5222":{
        "name":"环卫车工况(环卫面板_3)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"一次循环",
            1:"连续循环",
            2:"压板旋起",
            3:"滑板上行",
            4:"工作灯",
            5:"制动",
            6:"刮板压下",
            7:"滑板下行",
            8:"下降",
            9:"上升",
        })
    },
    "5223":{
        "name":"环卫车工况(环卫面板_4)",
        "len":4,
        "parser":lambda b:parse_work_status(b,{
            0:"排料模式开",
            1:"填料器举开",
            2:"推铲推出开",
            3:"清料开",
            4:"锁勾锁紧开",
            5:"填料下降开",
            6:"推铲收回开",
            7:"总电源开",
        })
    },
    "5224": {
        "name": "环卫车工况(环卫面板_4扩展)",
        "len": 4,
        "parser": lambda b: parse_work_status(b, {
            0: "电源开",
            1: "作业开始",
            2: "照明",
            3: "除尘",
            4: "左扫",
            5: "右扫",
            # BIT6: 1代表扫路，0代表洗扫
            6: { "name": "清扫模式", 0: "洗扫", 1: "扫路" }, 
            7: "纯洗",
            8: "喷雾",
            9: "自洁",
            # BIT10: 1代表强力，0代表标准
            10: { "name": "作业强度", 0: "标准", 1: "强力" }, 
            11: "左冲洗",
            12: "右冲洗",
            13: "垃圾桶开门",
            14: "垃圾桶倾翻",
            15: "垃圾桶关门",
            16: "垃圾桶回位",
            17: "开启语音",
            18: "开启音乐"
        })
    }
}

