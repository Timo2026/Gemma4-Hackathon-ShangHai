from sqlalchemy.orm import Session
from sqlmodel import select

from app.models.measure import Measure, MeasureCode


DEFAULT_MEASURES: tuple[tuple[MeasureCode, str, str], ...] = (
    (MeasureCode.CBP, "Controlling High Blood Pressure", "HEDIS blood pressure control measure."),
    (MeasureCode.BPD, "Blood Pressure Control for Patients With Diabetes", "HEDIS diabetes blood pressure control measure."),
    (MeasureCode.GSD, "Glycemic Status Assessment for Patients With Diabetes", "HEDIS HbA1c glycemic status measure."),
)


def seed_default_measures(session: Session) -> None:
    changed = False
    for code, name, description in DEFAULT_MEASURES:
        existing = session.execute(select(Measure).where(Measure.code == code)).scalars().first()
        if existing is not None:
            continue
        session.add(Measure(code=code, name=name, description=description))
        changed = True

    if changed:
        session.commit()
