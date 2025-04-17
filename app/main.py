from fastapi import FastAPI

app = FastAPI(
    title="DataPulse Backend",
    description="Backend API for the DataPulse analytics platform",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to DataPulse!"}
