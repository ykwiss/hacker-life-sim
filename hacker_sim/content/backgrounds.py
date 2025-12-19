"""Background definitions."""
BACKGROUNDS = {
    "nomad": {
        "label": "流浪脚本小子",
        "mods": {"nerve": 10, "economy": -10},
        "starting_skills": {"foundation": 1, "web": 1},
        "lore": "从网吧混到地下论坛的小子，胆量是唯一资产。",
    },
    "analyst": {
        "label": "安全分析师",
        "mods": {"intellect": 10, "ethics": 5, "exposure": 5},
        "starting_skills": {"foundation": 2},
        "lore": "白帽企业社畜，熟悉流程与报告套路。",
    },
    "freelancer": {
        "label": "自由渗透顾问",
        "mods": {"economy": 15, "discipline": 5},
        "starting_skills": {"foundation": 2, "web": 1},
        "lore": "长期漂泊的红队顾问，懂得向客户开价。",
    },
    "ghost": {
        "label": "地下情报员",
        "mods": {"nerve": 15, "ethics": -10},
        "starting_skills": {"foundation": 1, "social": 1},
        "lore": "深藏暗网的情报掮客，联系人遍布全球。",
    },
}
