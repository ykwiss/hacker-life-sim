"""Aggregated content registries."""
from .backgrounds import BACKGROUNDS
from .contracts import TASK_CONTRACTS
from .gear import GEAR_CATALOG
from .market import MARKET_TRENDS
from .training import TRAINING_MODULES
from .crisis import CRISIS_EVENTS

__all__ = [
    "BACKGROUNDS",
    "TRAINING_MODULES",
    "TASK_CONTRACTS",
    "GEAR_CATALOG",
    "MARKET_TRENDS",
    "CRISIS_EVENTS",
]
