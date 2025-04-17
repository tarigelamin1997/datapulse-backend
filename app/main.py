from fastapi import FastAPI
from app.api import auth
from app.db import user_model, database

user_model.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="DataPulse Backend")

app.include_router(auth.router, prefix="/auth")

@app.get("/")
def root():
    return {"message: Welcome to DataPulse!"}

from app.db import user_model, sales_model
from app.db.database import engine

user_model.Base.metadata.create_all(bind=engine)
sales_model.Base.metadata.create_all(bind=engine)

from app.api import dashboard
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
