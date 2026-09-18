from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.seed import seed_data
from app.routers import auth, users, cultures, greenhouses, resources, schedules, work_executions

app = FastAPI(
    title="Агрокомплекс — тепличное хозяйство",
    description="Учёт теплиц, культур, графика работ и фактического выполнения работ с расходом ресурсов.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cultures.router)
app.include_router(greenhouses.router)
app.include_router(resources.router)
app.include_router(schedules.router)
app.include_router(work_executions.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "agrocomplex-api"}
