
# 四废日
SI_FEI_RI = {
    "name": "四废日",
    "rules": [
        {
            "month_branch": {"寅","卯","辰"},
            "day": {"庚申","辛酉"}
        },
        {
            "month_branch": {"巳","午","未"},
            "day": {"壬子","癸亥"}
        }
    ],
    "intro": "月令与日柱相废"
}
# 魁罡
KUI_GANG = {
    "name": "魁罡",
    "rules": [
        {
            "day": {"庚辰", "庚戌", "壬辰", "壬戌"}
        }
    ],
    "intro": "日柱为庚辰、庚戌、壬辰、壬戌者，为魁罡日"
}

# 神煞
ALL_GODS = [
    SI_FEI_RI,  #四废日
    KUI_GANG    #魁罡
]
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
        if bazi.get(key) not in allowed:
            return False
    return True


def match_rules(bazi: dict, rules: list) -> bool:
    """多组 OR 规则"""
    for rule in rules:
        if match_rule_group(bazi, rule):
            return True
    return False


def is_si_fei_ri(bazi: dict) -> bool:
    return match_rules(bazi, SI_FEI_RI["rules"])

if __name__ == "__main__":
    bazi = {
    "year":  "戊午",
    "month": "壬寅",
    "day":   "庚申",
    "hour":  "戊寅",
    "year_stem":  "戊",
    "year_branch":"午",
    "month_stem": "壬",
    "month_branch":"寅",
    "day_stem":   "庚",
    "day_branch": "申",
    }
    bazi_Arr = [
        {"month_branch":"寅","day":"庚申"},
        {"day":"庚辰"},
        {"month_branch":"子","day":"甲子"},
    ]
    
    for _bazi in bazi_Arr:
        gods = find_gods(_bazi)
        for g in gods:
            print(f"{g['name']}：{g['intro']}")
        # print(f"{g['name']}：{g['intro']}")