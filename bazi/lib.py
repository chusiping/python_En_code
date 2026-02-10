
# 四废日
SI_FEI_RI = {
    "name": "四废日",
    "rules": [
        {"month_branch": {"寅","卯","辰"},"day": {"庚申","辛酉"}},
        {"month_branch": {"巳","午","未"},"day": {"壬子","癸亥"}}
    ],
    "intro": "月令与日柱相废"
}
# 魁罡
KUI_GANG = {
    "name": "魁罡",
    "rules": [{"day": {"庚辰", "庚戌", "壬辰", "壬戌"}}],
    "intro": "日柱为庚辰、庚戌、壬辰、壬戌者，为魁罡日"
}
# 羊刃
YANG_REN_MAP = {
    "甲": "卯",
    "乙": "寅",
    "丙": "午",
    "丁": "巳",
    "戊": "午",
    "己": "巳",
    "庚": "酉",
    "辛": "申",
    "壬": "子",
    "癸": "亥",
}

def match_yang_ren(bazi: dict) -> bool:
    """
    羊刃规则（第二层：映射型规则）
    """
    day_stem = bazi.get("day_stem")
    if not day_stem:
        return False

    yang_ren_branch = YANG_REN_MAP.get(day_stem)
    if not yang_ren_branch:
        return False

    # 命局中是否出现羊刃地支
    branches = {
        bazi.get("year_branch"),
        bazi.get("month_branch"),
        bazi.get("day_branch"),
        bazi.get("hour_branch"),
    }

    return yang_ren_branch in branches

YANG_REN = {
    "name": "羊刃",
    "type": "mapping",
    "match": match_yang_ren,
    "intro": "以日干为主，命局见其刃支者为羊刃"
}

# 神煞  四废日 魁罡 羊刃
ALL_GODS = [SI_FEI_RI, KUI_GANG,YANG_REN]

# 取神煞
def find_gods(bazi):
    result = []

    for g in ALL_GODS:
        # 第一层：集合规则
        if g.get("rules") and match_rules(bazi, g["rules"]):
            result.append({
                "name": g["name"],
                "intro": g.get("intro", "")
            })

        # 第二层：映射规则
        if g.get("type") == "mapping":
            if g["match"](bazi):
                result.append({
                    "name": g["name"],
                    "intro": g.get("intro", "")
                })

    return result

def match_rule_group(bazi: dict, rule: dict) -> bool:
    """单组 AND 规则"""
    for key, allowed in rule.items():
        key_ = bazi.get(key)     
        if key_ not in allowed:
            return False
    return True


def match_rules(bazi: dict, rules: list) -> bool:
    """多组 OR 规则"""
    for rule in rules:
        if match_rule_group(bazi, rule):
            return True
    return False

def convert_bazi(bazi_str):
    bazi_str = bazi_str.strip()
    if ',' in bazi_str:
        # 逗号分隔格式
        parts = [part.strip() for part in bazi_str.split(',')]
        if len(parts) != 4:
            raise ValueError("逗号分隔的八字必须包含4个部分")
        
        # 验证每个部分都是2个字符
        for i, part in enumerate(parts):
            if len(part) != 2:
                raise ValueError(f"第{i+1}柱'{part}'长度必须为2个字符")
        
        year, month, day, hour = parts
    else:
        # 连续格式
        if len(bazi_str) != 8:
            raise ValueError("连续格式八字字符串长度必须为8个字符")
        
        # 每两个字符为一柱
        year = bazi_str[0:2]
        month = bazi_str[2:4]
        day = bazi_str[4:6]
        hour = bazi_str[6:8]
    
    # 提取天干地支
    bazi = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "year_stem": year[0],      # 年干
        "year_branch": year[1],    # 年支
        "month_stem": month[0],    # 月干
        "month_branch": month[1],  # 月支
        "day_stem": day[0],        # 日干
        "day_branch": day[1],      # 日支
        "hour_stem": hour[0],      # 时干
        "hour_branch": hour[1]     # 时支
    }
    
    return bazi



if __name__ == "__main__":
    bazi1 = convert_bazi("戊午,壬寅,庚申,戊寅")
    bazi2 = convert_bazi("戊午,壬寅,庚戌,戊寅")
    bazi3 = convert_bazi("戊午,壬子,甲子,辛卯")

    bazi_Arr = [
        bazi1,bazi2,bazi3
    ]
    # for i, g in enumerate(bazi_Arr, start=1):  
    for i, _bazi in enumerate(bazi_Arr, start=1):
        gods = find_gods(_bazi)
        for g in gods:
            print(f"八字{i}.　　{g['name']}：{g['intro']}")