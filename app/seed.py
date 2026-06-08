from sqlalchemy.orm import Session

from app.models import Brand, Category, Subcategory


def seed_reference_data(db: Session) -> None:
    if db.query(Brand).count() == 0:
        db.add(
            Brand(
                brand_name="MedSupply Co",
                brand_gln="1234567890123",
                company_prefix="1234567",
                address="100 Healthcare Ave, Boston, MA",
            )
        )

    sensors = db.query(Category).filter(Category.name == "Sensors").first()
    if not sensors:
        sensors = Category(name="Sensors")
        db.add(sensors)
        db.flush()

        db.add(Subcategory(name="Oxygen sensor", category_id=sensors.id))

    db.commit()
