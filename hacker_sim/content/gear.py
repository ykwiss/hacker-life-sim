"""Gear registry."""
from ..models import GearItem

GEAR_CATALOG = [
    GearItem(
        item_id="rig_basic",
        name="裂相笔记本",
        cost=2500,
        bonuses={"hardware": 1, "intellect": 2},
        category="hardware",
        description="定制散热与低噪音设计，提高分析效率。",
    ),
    GearItem(
        item_id="vpn_mesh",
        name="Mesh隐匿网络",
        cost=3200,
        bonuses={"network": 2, "exposure": -5},
        category="network",
        description="多层代理与量子随机路由，降低追踪概率。",
    ),
    GearItem(
        item_id="forge_lab",
        name="Exploit锻炉",
        cost=7800,
        bonuses={"binary": 1, "research_points": 2},
        category="lab",
        description="包含定制VM农场与自动化脚本生成工具。",
    ),
    GearItem(
        item_id="holo_ops",
        name="Holo Ops 情报桌",
        cost=5400,
        bonuses={"social": 1, "exposure": -3},
        category="intel",
        description="可视化人脉网与钓鱼剧本模拟器，提升社工效率。",
    ),
    GearItem(
        item_id="nebula_stack",
        name="Nebula云栈",
        cost=6900,
        bonuses={"cloud": 1, "hardware": 1},
        category="cloud",
        description="预装Terraform实验环境与本地K8s集群。",
    ),
]
