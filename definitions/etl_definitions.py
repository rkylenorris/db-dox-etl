from pathlib import Path
from dataclasses import dataclass
from typing import Final, Iterable
import json

# ETL Definitions Path
etl_defs_path: Path = Path("definitions\\etl_steps_and_phases.json")


# ETL Phase Definition Dataclass
@dataclass(frozen=True)
class EtlPhaseDefinition:
    id: int
    key: str
    name: str
    description: str | None = None


# ETL Step Definition Dataclass
@dataclass(frozen=True)
class EtlStepDefinition:
    id: int
    phase_id: int
    key: str
    name: str
    code: str
    description: str | None = None


# Load ETL Definitions from JSON
etl_definitions = json.loads(etl_defs_path.read_text())

# Create Lists of Phase and Step Definitions
PHASES: Final[list[EtlPhaseDefinition]] = [
    EtlPhaseDefinition(**phase) for phase in etl_definitions["phases"]
]
STEPS: Final[list[EtlStepDefinition]] = [
    EtlStepDefinition(**step) for step in etl_definitions["steps"]
]

# Convenience lookup by key and id (useful both in app code and tests).
PHASE_BY_KEY: Final[dict[str, EtlPhaseDefinition]] = {p.key: p for p in PHASES}
PHASE_BY_ID: Final[dict[int, EtlPhaseDefinition]] = {p.id: p for p in PHASES}

STEP_BY_KEY: Final[dict[str, EtlStepDefinition]] = {s.key: s for s in STEPS}
STEP_BY_ID: Final[dict[int, EtlStepDefinition]] = {s.id: s for s in STEPS}


def iter_steps_in_phase(phase_key: str) -> Iterable[EtlStepDefinition]:
    """Yield all ETL steps belonging to the specified phase key."""
    phase = PHASE_BY_KEY[phase_key]

    return (step for step in STEPS if step.phase_id == phase.id)


def get_phase_of_step(step: EtlStepDefinition) -> EtlPhaseDefinition:
    """Get the ETL phase definition for the given step key."""
    phase = PHASE_BY_ID[step.phase_id]
    return phase


if __name__ == "__main__":
    # Example usage: print all phases and their steps
    print("ETL Phases and Steps:")
    for phase in PHASES:
        print(f"Phase: {phase.name}, (ID: {phase.id})")
        for step in iter_steps_in_phase(phase.key):
            print(f"\tStep: {step.name} (ID: {step.id}, Code: {step.code})")
        print()
        print("-" * 40)
        print()
