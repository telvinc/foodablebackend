from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import ai as ai_router

from database import Base, engine, SessionLocal
from routers import groceries
try:
    from routers import recipes as recipes_router
    HAS_RECIPES = True
except Exception:
    HAS_RECIPES = False

from seed_data import seed_groceries, seed_recipes

from routers.debug import router as debug_router


app = FastAPI(title="Foodable Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(debug_router)


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
