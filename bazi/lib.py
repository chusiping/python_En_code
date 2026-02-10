
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

# 神煞  四废日 魁罡
ALL_GODS = [SI_FEI_RI, KUI_GANG]

# 取神煞
def find_gods(bazi):
    result = []
    for g in ALL_GODS:
        if match_rules(bazi, g["rules"]):
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
    bazi = convert_bazi("戊午,壬寅,庚申,戊寅")
    bazi_Arr = [
        bazi,
        {"day":"庚辰"},
        {"month_branch":"子","day":"甲子"},
    ]
    
    for _bazi in bazi_Arr:
        gods = find_gods(_bazi)
        for g in gods:
            print(f"{g['name']}：{g['intro']}")
        # print(f"{g['name']}：{g['intro']}")