from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def home():
    return {"message": "ESP32 server is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
