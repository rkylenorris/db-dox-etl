from enum import Enum


class JobEnv(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class RunTriggerType(Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"


class Status(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
