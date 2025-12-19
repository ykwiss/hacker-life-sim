"""Core dataclasses for Hacker Life Sandbox."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Attributes:
    intellect: int = 45
    discipline: int = 40
    ethics: int = 55
    nerve: int = 40
    economy: int = 30
    exposure: int = 5


@dataclass
class Reputation:
    white_hat: int = 10
    black_hat: int = 10
    corporate: int = 5
    law_watch: int = 0
    public: int = 0


@dataclass
class Resources:
    credits: int = 5000
    hardware: int = 1
    network: int = 1
    research_points: int = 0


@dataclass
class Player:
    codename: str
    background: str
    attributes: Attributes = field(default_factory=Attributes)
    reputation: Reputation = field(default_factory=Reputation)
    resources: Resources = field(default_factory=Resources)
    skills: Dict[str, int] = field(default_factory=lambda: {
        "foundation": 1,
        "web": 0,
        "binary": 0,
        "mobile": 0,
        "social": 0,
        "cloud": 0,
    })
    unlocked_nodes: List[str] = field(default_factory=lambda: ["training_intro"])
    age: int = 10
    events_since_age: int = 0
    day: int = 1
    hour: int = 9
    log: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "codename": self.codename,
            "background": self.background,
            "attributes": self.attributes.__dict__,
            "reputation": self.reputation.__dict__,
            "resources": self.resources.__dict__,
            "skills": self.skills,
            "unlocked_nodes": self.unlocked_nodes,
            "age": self.age,
            "events_since_age": self.events_since_age,
            "day": self.day,
            "hour": self.hour,
            "log": self.log[-40:],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Player":
        attr = Attributes(**payload.get("attributes", {}))
        rep = Reputation(**payload.get("reputation", {}))
        res = Resources(**payload.get("resources", {}))
        player = cls(
            codename=payload.get("codename", "Unknown"),
            background=payload.get("background", "nomad"),
            attributes=attr,
            reputation=rep,
            resources=res,
        )
        player.skills = payload.get("skills", player.skills)
        player.unlocked_nodes = payload.get("unlocked_nodes", player.unlocked_nodes)
        player.age = payload.get("age", player.age)
        player.events_since_age = payload.get("events_since_age", 0)
        player.day = payload.get("day", player.day)
        player.hour = payload.get("hour", player.hour)
        player.log = payload.get("log", [])
        return player


@dataclass
class TrainingModule:
    module_id: str
    title: str
    tier: int
    category: str
    base_success: float
    cost: int
    hours: int
    skill_gain: Dict[str, int]
    description: str


@dataclass
class TaskContract:
    contract_id: str
    name: str
    legality: str
    risk: str
    payout_range: List[int]
    requirements: Dict[str, int]
    description: str


@dataclass
class GearItem:
    item_id: str
    name: str
    cost: int
    bonuses: Dict[str, int]
    category: str
    description: str


@dataclass
class MarketSnapshot:
    lawful_multiplier: float
    underground_multiplier: float
    enforcement_level: int
    trend: str

@dataclass
class CrisisOption:
    label: str
    base_success: float
    requirement: Optional[str]
    success_delta: Dict[str, int]
    failure_delta: Dict[str, int]
    description: str


@dataclass
class CrisisEvent:
    event_id: str
    title: str
    trigger: str
    difficulty: str
    options: List[CrisisOption]

