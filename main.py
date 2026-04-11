from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI()

DATA_FILE = "sensor_data.json"


class SensorData(BaseModel):
    temperature: float
    humidity: float
    soil: int


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"content": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"content": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.get("/")
def home():
    return {"message": "Server işləyir qaqa"}


@app.post("/api/data")
def receive_data(sensor: SensorData):
    data = load_data()

    new_record = {
        "temperature": sensor.temperature,
        "humidity": sensor.humidity,
        "soil": sensor.soil,
        "timestamp": datetime.now().isoformat()
    }

    data["content"].append(new_record)
    save_data(data)

    return {
        "status": "success",
        "message": "Data yadda saxlanıldı",
        "received": new_record
    }


@app.get("/api/data")
def get_data():
    return load_data()
