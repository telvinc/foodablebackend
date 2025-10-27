from fastapi import FastAPI
from database import Base, engine
from routers import groceries 

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Foodable Backend")

app.include_router(groceries.router)

@app.get("/")
def root():
    return {"message": "backend works"}
