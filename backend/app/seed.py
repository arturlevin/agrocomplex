from sqlalchemy.orm import Session

from app import models
from app.security import hash_password


def seed_data(db: Session):
    if db.query(models.User).count() > 0:
        return  # уже инициализировано

    chief = models.User(
        full_name="Иванов Иван Иванович",
        email="chief@agrocomplex.ru",
        role=models.UserRole.chief_agronomist,
        hashed_password=hash_password("chief123"),
    )
    agronomist1 = models.User(
        full_name="Петров Петр Петрович",
        email="petrov@agrocomplex.ru",
        role=models.UserRole.agronomist,
        hashed_password=hash_password("agro123"),
    )
    agronomist2 = models.User(
        full_name="Сидорова Анна Сергеевна",
        email="sidorova@agrocomplex.ru",
        role=models.UserRole.agronomist,
        hashed_password=hash_password("agro123"),
    )
    db.add_all([chief, agronomist1, agronomist2])

    tomato = models.Culture(name="Томат", description="Тепличный томат, сорт индетерминантный")
    cucumber = models.Culture(name="Огурец", description="Тепличный огурец, партенокарпический гибрид")
    pepper = models.Culture(name="Перец сладкий", description="Тепличный сладкий перец")
    db.add_all([tomato, cucumber, pepper])
    db.flush()

    gh1 = models.Greenhouse(name="Теплица №1", culture_id=tomato.id, area_m2=500)
    gh2 = models.Greenhouse(name="Теплица №2", culture_id=cucumber.id, area_m2=450)
    gh3 = models.Greenhouse(name="Теплица №3", culture_id=pepper.id, area_m2=300)
    db.add_all([gh1, gh2, gh3])

    water = models.Resource(name="Вода", unit="л")
    npk = models.Resource(name="Удобрение NPK", unit="кг")
    seeds = models.Resource(name="Семена", unit="г")
    biofungicide = models.Resource(name="Биофунгицид", unit="л")
    db.add_all([water, npk, seeds, biofungicide])

    db.commit()
