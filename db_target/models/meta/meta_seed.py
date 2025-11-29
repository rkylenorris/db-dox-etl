from db_target import get_db_session
from definitions import PHASES, STEPS, PHASE_BY_ID, EtlPhaseDefinition, EtlStepDefinition

from db_target.models.meta.meta import ETLPhase, ETLStep as ETLStepModel


SESSION = get_db_session()


def add_phase(phase_def: EtlPhaseDefinition) -> ETLPhase:
    """
    Add an ETL phase if it does not already exist.
    Args:
        phase_name (str): Name of the ETL phase.
        description (str | None): Optional description of the phase.
    Returns:
        ETLPhase: The existing or newly created ETLPhase object."""
    phase = SESSION.query(ETLPhase).filter(
        ETLPhase.name == phase_def.name).one_or_none()
    if phase is None:
        phase = ETLPhase(id=phase_def.id, name=phase_def.name,
                         description=phase_def.description)
        SESSION.add(phase)
        SESSION.commit()
    return phase


def add_step(step_def: EtlStepDefinition, phase: ETLPhase) -> ETLStepModel:
    """
    Add an ETL step if it does not already exist.
    Args:
        step_name (str): Name of the ETL step.
        step_code (str): Code of the ETL step.
        phase (ETLPhase): The ETLPhase object this step belongs to.
        description (str | None): Optional description of the step.
    Returns:
        ETLStepModel: The existing or newly created ETLStep object."""
    step = SESSION.query(ETLStepModel).filter(
        ETLStepModel.name == step_def.name).one_or_none()
    if step is None:
        step = ETLStepModel(phase_id=phase.id, name=step_def.name,
                            code=step_def.code, phase=phase,
                            description=step_def.description)
        SESSION.add(step)
        SESSION.commit()
    return step


def seed_etl_phases_and_steps() -> None:
    """
    Seed the ETLPhase and ETLStep tables based on the EtlStep enum.
    This function checks for existing phases and steps to avoid duplicates.
    """

    current_phase: EtlPhaseDefinition | None = None

    for step_def in STEPS:
        phase_def = PHASE_BY_ID[step_def.phase_id]
        if current_phase is None or current_phase != phase_def:
            current_phase = phase_def
            phase = add_phase(phase_def)

        add_step(step_def, phase)

    SESSION.close()
