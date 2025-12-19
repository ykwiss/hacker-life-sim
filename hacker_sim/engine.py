"""Simulation engine for the hacker sandbox."""
from __future__ import annotations

import operator
import random
from typing import Dict, List, Optional, Tuple

from .content import BACKGROUNDS, CRISIS_EVENTS, GEAR_CATALOG, MARKET_TRENDS, TASK_CONTRACTS, TRAINING_MODULES
from .models import CrisisEvent, GearItem, MarketSnapshot, Player, TaskContract, TrainingModule


class GameEngine:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.rng = random.Random(seed)
        self.player: Optional[Player] = None
        self.market_index = 0
        self.active_crisis: Optional[CrisisEvent] = None

    # ------------------------------------------------------------------
    # Player lifecycle
    def create_player(self, codename: str, background_key: str) -> Player:
        if background_key not in BACKGROUNDS:
            raise ValueError("未知背景")
        profile = BACKGROUNDS[background_key]
        player = Player(codename=codename or "Zero", background=background_key)
        for attr, delta in profile["mods"].items():
            setattr(player.attributes, attr, max(0, getattr(player.attributes, attr) + delta))
        for skill, value in profile.get("starting_skills", {}).items():
            player.skills[skill] = value
        player.log.append("接入成功：{}".format(profile["label"]))
        self.player = player
        return player

    # ------------------------------------------------------------------
    # Training
    def export_state(self) -> dict:
        if not self.player:
            raise RuntimeError("无法保存：未创建角色")
        return {
            "player": self.player.to_dict(),
            "market_index": self.market_index,
        }

    def import_state(self, payload: dict) -> None:
        player_data = payload.get("player")
        if not player_data:
            raise RuntimeError("存档损坏")
        self.player = Player.from_dict(player_data)
        self.market_index = payload.get("market_index", 0)
        self.active_crisis = None
    def list_training(self) -> List[TrainingModule]:
        return TRAINING_MODULES

    def run_training(self, module_id: str) -> Tuple[bool, str]:
        self._require_player()
        module = next((mod for mod in TRAINING_MODULES if mod.module_id == module_id), None)
        if not module:
            raise ValueError("未知训练模块")
        if self.player.resources.credits < module.cost:
            raise RuntimeError("资金不足")
        self.player.resources.credits -= module.cost
        roll = self._training_success(module)
        self._advance_time(module.hours)
        if roll:
            for skill, inc in module.skill_gain.items():
                self.player.skills[skill] = min(10, self.player.skills.get(skill, 0) + inc)
            self.player.resources.research_points += 1
            msg = f"完成训练《{module.title}》"
        else:
            msg = f"训练失败《{module.title}》，需要复盘"
        self._log(msg)
        self._check_crisis_flags()
        return roll, msg

    def _training_success(self, module: TrainingModule) -> bool:
        intellect = self.player.attributes.intellect / 100
        discipline = self.player.attributes.discipline / 100
        base = module.base_success
        bonus = 0.05 * intellect + 0.03 * discipline + self.player.resources.hardware * 0.01
        penalty = max(0, (self.player.attributes.exposure - 20) * 0.002)
        chance = max(0.2, min(0.98, base + bonus - penalty))
        return self.rng.random() < chance

    # ------------------------------------------------------------------
    # Contracts
    def list_contracts(self, legality: Optional[str] = None) -> List[TaskContract]:
        contracts = TASK_CONTRACTS
        if self.player:
            filtered = [c for c in contracts if self._contract_visible(c)]
            if filtered:
                contracts = filtered
        if legality:
            contracts = [c for c in contracts if c.legality == legality]
        return contracts

    def _contract_visible(self, contract: TaskContract) -> bool:
        if not self.player:
            return True
        worst_gap = max((req - self.player.skills.get(skill, 0)) for skill, req in contract.requirements.items()) if contract.requirements else 0
        if worst_gap > 2:
            return False
        if self.player.age < 14 and contract.risk == "high":
            return False
        if self.player.reputation.law_watch > 40 and contract.legality == "illegal" and contract.risk == "high":
            return False
        return True

    def start_contract(self, contract_id: str) -> str:
        self._require_player()
        contract = next((c for c in TASK_CONTRACTS if c.contract_id == contract_id), None)
        if not contract:
            raise ValueError("未知契约")
        if not self._meets_requirements(contract.requirements):
            raise RuntimeError("技能不足")
        success = self._contract_success(contract)
        snapshot = self._market_snapshot()
        payout_multiplier = snapshot.lawful_multiplier if contract.legality == "lawful" else snapshot.underground_multiplier
        payout = self.rng.randint(*contract.payout_range)
        payout = int(payout * payout_multiplier)
        self._advance_time(self.rng.randint(4, 10))
        if success:
            self.player.resources.credits += payout
            self._adjust_rep(contract, True)
            msg = f"完成任务《{contract.name}》，收入¥{payout}" if contract.legality == "lawful" else f"成功执行地下委托《{contract.name}》，收益¥{payout}"
        else:
            loss = payout // 4
            self.player.resources.credits = max(0, self.player.resources.credits - loss)
            self._adjust_rep(contract, False)
            self.player.attributes.exposure += 5 if contract.legality == "illegal" else 2
            msg = f"任务失败《{contract.name}》，损失¥{loss}" if loss else f"任务失败《{contract.name}》"
        self._log(msg)
        self._maybe_trigger_crisis(contract, success)
        self._check_crisis_flags()
        return msg

    def _contract_success(self, contract: TaskContract) -> bool:
        base = 0.6
        skill_bonus = sum(self.player.skills.get(skill, 0) - need for skill, need in contract.requirements.items()) * 0.04
        gear_bonus = (self.player.resources.hardware + self.player.resources.network) * 0.02
        risk_penalty = {"low": 0.0, "medium": 0.08, "high": 0.18}.get(contract.risk, 0.1)
        exposure_penalty = self.player.attributes.exposure * 0.002
        law_penalty = self.player.reputation.law_watch * 0.003 if contract.legality == "illegal" else 0.0
        chance = max(0.1, min(0.95, base + skill_bonus + gear_bonus - risk_penalty - exposure_penalty - law_penalty))
        return self.rng.random() < chance

    def _adjust_rep(self, contract: TaskContract, success: bool) -> None:
        delta = 10 if success else -7
        if contract.legality == "lawful":
            self.player.reputation.white_hat = max(0, self.player.reputation.white_hat + delta)
            self.player.reputation.corporate = max(0, self.player.reputation.corporate + delta // 2)
            self.player.reputation.public = max(-100, min(100, self.player.reputation.public + (5 if success else -5)))
            self.player.reputation.law_watch = max(0, self.player.reputation.law_watch - (4 if success else 0))
        else:
            self.player.reputation.black_hat = max(0, self.player.reputation.black_hat + delta)
            self.player.reputation.law_watch += 6 if success else 3
            self.player.reputation.public = max(-100, min(100, self.player.reputation.public - (8 if success else 5)))

    def _maybe_trigger_crisis(self, contract: TaskContract, success: bool) -> None:
        if self.active_crisis:
            return
        if contract.legality == "illegal" and success and self.player.reputation.law_watch > 25:
            self._set_crisis("law_trace")

    # ------------------------------------------------------------------
    # Gear
    def list_gear(self) -> List[GearItem]:
        return GEAR_CATALOG

    def purchase_gear(self, item_id: str) -> str:
        self._require_player()
        item = next((g for g in GEAR_CATALOG if g.item_id == item_id), None)
        if not item:
            raise ValueError("未知装备")
        if self.player.resources.credits < item.cost:
            raise RuntimeError("资金不足")
        self.player.resources.credits -= item.cost
        for key, value in item.bonuses.items():
            if hasattr(self.player.attributes, key):
                setattr(self.player.attributes, key, getattr(self.player.attributes, key) + value)
            elif hasattr(self.player.resources, key):
                setattr(self.player.resources, key, getattr(self.player.resources, key) + value)
            elif key in self.player.skills:
                self.player.skills[key] = min(10, self.player.skills[key] + value)
        msg = f"购入 {item.name}"
        self._log(msg)
        self._check_crisis_flags()
        return msg

    # ------------------------------------------------------------------
    # Market + crisis
    def advance_market(self) -> MarketSnapshot:
        self.market_index = (self.market_index + 1) % len(MARKET_TRENDS)
        trend = MARKET_TRENDS[self.market_index]
        snapshot = MarketSnapshot(
            lawful_multiplier=trend["lawful"],
            underground_multiplier=trend["underground"],
            enforcement_level=trend["enforcement"],
            trend=trend["trend"],
        )
        self._log(f"市场变化：{trend['name']}")
        self._check_crisis_flags()
        return snapshot

    def _market_snapshot(self) -> MarketSnapshot:
        trend = MARKET_TRENDS[self.market_index]
        return MarketSnapshot(
            lawful_multiplier=trend["lawful"],
            underground_multiplier=trend["underground"],
            enforcement_level=trend["enforcement"],
            trend=trend["trend"],
        )

    # Crisis management
    def get_active_crisis(self) -> Optional[CrisisEvent]:
        return self.active_crisis

    def resolve_crisis(self, option_index: int) -> Tuple[bool, str]:
        self._require_player()
        if not self.active_crisis:
            raise RuntimeError("当前没有危机")
        crisis = self.active_crisis
        if option_index < 0 or option_index >= len(crisis.options):
            raise ValueError("非法选项")
        option = crisis.options[option_index]
        chance = option.base_success + self._crisis_requirement_bonus(option.requirement)
        chance = max(0.05, min(0.95, chance))
        success = self.rng.random() < chance
        delta = option.success_delta if success else option.failure_delta
        self._apply_delta_map(delta)
        msg = f"危机《{crisis.title}》{'化解' if success else '处理失败'}"
        self._log(msg)
        self.active_crisis = None
        self._check_crisis_flags()
        return success, msg

    def _apply_delta_map(self, delta: Dict[str, int]) -> None:
        for key, change in delta.items():
            if hasattr(self.player.attributes, key):
                setattr(self.player.attributes, key, getattr(self.player.attributes, key) + change)
            elif hasattr(self.player.reputation, key):
                setattr(self.player.reputation, key, getattr(self.player.reputation, key) + change)
            elif hasattr(self.player.resources, key):
                setattr(self.player.resources, key, getattr(self.player.resources, key) + change)
            elif key in self.player.skills:
                self.player.skills[key] = max(0, min(10, self.player.skills[key] + change))

    def _crisis_requirement_bonus(self, requirement: Optional[str]) -> float:
        if not requirement or not self.player:
            return 0.0
        if requirement in self.player.skills:
            return self.player.skills[requirement] * 0.05
        if requirement == "network":
            return self.player.resources.network * 0.04
        if requirement == "foundation":
            return self.player.skills.get("foundation", 0) * 0.04
        return 0.0

    def _check_crisis_flags(self) -> None:
        if not self.player or self.active_crisis:
            return
        for event in CRISIS_EVENTS:
            if self._crisis_condition(event.trigger):
                self.active_crisis = event
                self._log(f"危机触发：{event.title}")
                break

    def _crisis_condition(self, expr: str) -> bool:
        if expr.startswith("law_watch"):
            op_char = ">" if ">" in expr else "<"
            lhs, rhs = expr.split(op_char)
            value = int(rhs)
            current = self.player.reputation.law_watch
            return (operator.gt if op_char == ">" else operator.lt)(current, value)
        if expr == "market_high":
            return self.market_index == len(MARKET_TRENDS) - 1
        return False

    def _set_crisis(self, event_id: str) -> None:
        if self.active_crisis:
            return
        crisis = next((evt for evt in CRISIS_EVENTS if evt.event_id == event_id), None)
        if crisis:
            self.active_crisis = crisis
            self._log(f"危机触发：{crisis.title}")

    # ------------------------------------------------------------------
    def _advance_time(self, hours: int) -> None:
        self.player.hour += hours
        while self.player.hour >= 24:
            self.player.hour -= 24
            self.player.day += 1
            self.player.attributes.exposure = max(0, self.player.attributes.exposure - 1)

    def _meets_requirements(self, reqs: Dict[str, int]) -> bool:
        return all(self.player.skills.get(skill, 0) >= level for skill, level in reqs.items())

    def _log(self, message: str) -> None:
        if self.player:
            self.player.log.append(message)
            self.player.events_since_age += 1
            if self.player.events_since_age >= 12:
                self.player.events_since_age = 0
                self.player.age += 1
                self.player.log.append(f"年岁增长：{self.player.age} 岁")
            if len(self.player.log) > 80:
                self.player.log.pop(0)

    def _require_player(self) -> None:
        if not self.player:
            raise RuntimeError("需要先创建角色")
