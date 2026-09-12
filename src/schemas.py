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


class TireRisk(str, Enum):
    """Application-owned tire degradation risk levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TireAction(str, Enum):
    """Bounded tire-management actions emitted by the tire analyst."""

    MAINTAIN = "Maintain"
    MANAGE = "Manage"
    PREPARE_TO_PIT = "Prepare to Pit"


class PaceStatus(str, Enum):
    """Application-owned pace performance states."""

    ON_TARGET = "On Target"
    DEGRADED = "Degraded"
    CRITICAL = "Critical"


class PaceAction(str, Enum):
    """Bounded pace-management actions emitted by the pace analyst."""

    MAINTAIN = "Maintain"
    REVIEW = "Review Pace Loss"
    MANAGE = "Manage and Reassess"


class StrategyAction(str, Enum):
    """Application-owned final actions published by the strategy orchestrator."""

    MAINTAIN = "Maintain"
    REVIEW = "Review Strategy"
    MANAGE = "Manage and Reassess"
    PREPARE_TO_PIT = "Prepare to Pit"


class VerificationStatus(str, Enum):
    """Application-owned publication verification states."""

    APPROVED = "Approved"
    REJECTED = "Rejected"


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


class TireAssessment(BaseModel):
    """Validated output contract for deterministic tire analysis."""

    model_config = ConfigDict(extra="forbid")

    risk: TireRisk
    action: TireAction
    estimated_remaining_laps: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=1)


class PaceAssessment(BaseModel):
    """Validated output contract for deterministic pace analysis."""

    model_config = ConfigDict(extra="forbid")

    status: PaceStatus
    action: PaceAction
    target_lap_time: float = Field(gt=0)
    delta_to_target: float
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=1)


class OrchestratedStrategy(BaseModel):
    """Validated publication contract for the centralized strategy orchestrator."""

    model_config = ConfigDict(extra="forbid")

    telemetry: TelemetrySnapshot
    rules: RulesStrategy
    tire: TireAssessment
    pace: PaceAssessment
    final_action: StrategyAction
    priority: StrategyPriority
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str = Field(min_length=1)


class StrategyVerification(BaseModel):
    """Validated decision produced by the publication verifier."""

    model_config = ConfigDict(extra="forbid")

    status: VerificationStatus
    publishable: bool
    checks_run: int = Field(ge=1)
    violations: list[str]
    rationale: str = Field(min_length=1)
