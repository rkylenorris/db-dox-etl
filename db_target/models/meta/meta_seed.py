from db_target import get_db_session

from db_target.models.meta.meta import ETLPhase, ETLStep as ETLStepModel

from etl_logging.etl_step import EtlStep, step_to_str, get_phase_from_step, normalize_step_name


SESSION = get_db_session()


def add_phase(phase_name: str, description: str | None = None) -> ETLPhase:
    """
    Add an ETL phase if it does not already exist.
    Args:
        phase_name (str): Name of the ETL phase.
        description (str | None): Optional description of the phase.
    Returns:
        ETLPhase: The existing or newly created ETLPhase object."""
    phase = SESSION.query(ETLPhase).filter(
        ETLPhase.name == phase_name).one_or_none()
    if phase is None:
        phase = ETLPhase(name=phase_name, description=description)
        SESSION.add(phase)
        SESSION.commit()
    return phase


def add_step(step_name: str, step_code: str, phase: ETLPhase, description: str | None = None) -> ETLStepModel:
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
        ETLStepModel.name == step_name).one_or_none()
    if step is None:
        step = ETLStepModel(phase_id=phase.id, name=step_name,
                            code=step_code, phase=phase,
                            description=description)
        SESSION.add(step)
        SESSION.commit()
    return step


def seed_etl_phases_and_steps() -> None:
    """
    Seed the ETLPhase and ETLStep tables based on the EtlStep enum.
    This function checks for existing phases and steps to avoid duplicates.
    """

    current_phase = None

    for step in EtlStep:
        step_name = normalize_step_name(step.name)
        step_code = step_to_str(step)
        phase_name = get_phase_from_step(step)

        if current_phase is None or current_phase.name != phase_name:
            current_phase = add_phase(phase_name)

        add_step(step_name, step_code, current_phase)

    SESSION.close()
