from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import ai as ai_router

from database import Base, engine, SessionLocal
from routers import groceries
try:
    from routers import recipes as recipes_router  # noqa
    HAS_RECIPES = True
except Exception:
    HAS_RECIPES = False

from seed_data import seed_groceries, seed_recipes

app = FastAPI(title="Foodable Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groceries.router)
if HAS_RECIPES:
    app.include_router(recipes_router.router)

app.include_router(ai_router.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_groceries(db)
        seed_recipes(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "backend works"}
