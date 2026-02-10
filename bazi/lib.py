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
    "intro": "四废日：月令与日柱相废"
}

ALL_GODS = [
    SI_FEI_RI,
    # YANG_REN,
    # KUI_GANG,
]

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

