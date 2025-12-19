"""Crisis registry."""
from ..models import CrisisEvent, CrisisOption

CRISIS_EVENTS = [
    CrisisEvent(
        event_id="law_trace",
        title="执法监控升级",
        trigger="law_watch>30",
        difficulty="medium",
        options=[
            CrisisOption(
                label="切断链路并冷却",
                base_success=0.65,
                requirement=None,
                success_delta={"exposure": -8},
                failure_delta={"exposure": 5, "law_watch": 5},
                description="暂停所有行动，花时间清理日志。",
            ),
            CrisisOption(
                label="社工误导",
                base_success=0.55,
                requirement="social",
                success_delta={"law_watch": -10},
                failure_delta={"law_watch": 8, "public": -5},
                description="利用社工联系人转移执法注意力。",
            ),
        ],
    ),
    CrisisEvent(
        event_id="market_crash",
        title="漏洞市场崩盘",
        trigger="market_high",
        difficulty="low",
        options=[
            CrisisOption(
                label="抛售存货",
                base_success=0.7,
                requirement=None,
                success_delta={"credits": 3000},
                failure_delta={"credits": -1500},
                description="在崩盘完全爆发前脱手手中0day。",
            ),
            CrisisOption(
                label="等待反弹",
                base_success=0.5,
                requirement="foundation",
                success_delta={"public": 5, "credits": 2000},
                failure_delta={"credits": -2000},
                description="公开漏洞细节换取白帽尊重，赌后续顾问单。",
            ),
        ],
    ),
]
