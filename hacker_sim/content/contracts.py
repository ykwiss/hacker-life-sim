"""Contract registry."""
from ..models import TaskContract

TASK_CONTRACTS = [
    TaskContract(
        contract_id="bb_light",
        name="赏金：电商信息泄露",
        legality="lawful",
        risk="low",
        payout_range=[1500, 4200],
        requirements={"web": 1},
        description="购物站点怀疑存在目录遍历，提交完整复现即可。",
    ),
    TaskContract(
        contract_id="corp_assess",
        name="企业渗透评估",
        legality="lawful",
        risk="medium",
        payout_range=[6000, 15000],
        requirements={"web": 2, "foundation": 2},
        description="完成外网攻防与报告，时间紧迫。",
    ),
    TaskContract(
        contract_id="cloud_guard",
        name="云靶场护航",
        legality="lawful",
        risk="medium",
        payout_range=[9000, 20000],
        requirements={"cloud": 1, "foundation": 2},
        description="为金融机构审计容器集群与S3策略。",
    ),
    TaskContract(
        contract_id="datavault",
        name="地下委托：攻破CRM",
        legality="illegal",
        risk="high",
        payout_range=[20000, 42000],
        requirements={"web": 2, "social": 1},
        description="掩护雇主窃取数百万用户资料，风险巨大。",
    ),
    TaskContract(
        contract_id="zero_drop",
        name="0day 暗网售卖",
        legality="illegal",
        risk="high",
        payout_range=[28000, 60000],
        requirements={"binary": 1, "foundation": 3},
        description="自研漏洞可高价出售，但执法注意力极高。",
    ),
]
