from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TrackCondition(str, Enum):
    """Allowed track-surface states for the current simulation."""

    DRY = "Dry"
    WET = "Wet"


class StrategyPriority(str, Enum):
    """Application-owned priority levels for deterministic strategy output."""

    NORMAL = "Normal"
    HIGH = "High"


class TelemetrySnapshot(BaseModel):
    """Validated telemetry for one simulated race lap."""

    model_config = ConfigDict(extra="forbid")

    lap: int = Field(ge=1)
    lap_time: float = Field(gt=0)
    tire_temp: float = Field(ge=0)
    fuel_level: float = Field(ge=0, le=100)
    track_condition: TrackCondition


class RulesStrategy(BaseModel):
    """Validated output contract for the deterministic strategy engine."""

    model_config = ConfigDict(extra="forbid")

    priority: StrategyPriority
    recommendation: str = Field(min_length=1)
