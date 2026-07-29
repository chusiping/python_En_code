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
            "value":(int.from_bytes(b,"big") & 0x7FFF)/10,
            "unit":"L" if int.from_bytes(b,"big")&0x8000 else "%"
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


    "5112":{
        "name":"MIL状态",
        "len":1,
        "parser":lambda b:"点亮" if b[0]==1 else "未点亮"
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
    }
}

