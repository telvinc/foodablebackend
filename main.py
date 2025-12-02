from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from routers import ai as ai_router
from routers import auth as auth_router
from routers import community as community_router
from routers import groceries
try:
    from routers import recipes as recipes_router
    HAS_RECIPES = True
except Exception:
    HAS_RECIPES = False

from routers.debug import router as debug_router

# DB + Seed
from database import Base, engine, SessionLocal
from seed_data import seed_groceries, seed_recipes


app = FastAPI(title="Foodable Backend", version="0.2.0")

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # update later for prod if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Include Routers -----
app.include_router(debug_router)

app.include_router(groceries.router)

if HAS_RECIPES:
    app.include_router(recipes_router.router)

app.include_router(ai_router.router)

# NEW ROUTES (auth + community)
app.include_router(auth_router.router)
app.include_router(community_router.router)


# ----- Startup -----
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_groceries(db)
        seed_recipes(db)
    finally:
        db.close()


# ----- Root -----
@app.get("/")
def root():
    return {"message": "backend works"}
