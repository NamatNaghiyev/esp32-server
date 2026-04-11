from fastapi import FastAPI, Query
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


@app.get("/api/data/latest")
def get_latest_data():
    data = load_data()
    content = data.get("content", [])

    if not content:
        return {"status": "empty", "message": "Hələ data yoxdur"}

    return {
        "status": "success",
        "latest": content[-1]
    }


@app.get("/api/data/by-date")
def get_data_by_date(date: str = Query(..., description="Format: YYYY-MM-DD")):
    data = load_data()
    content = data.get("content", [])

    filtered = [
        item for item in content
        if item.get("timestamp", "").startswith(date)
    ]

    return {
        "status": "success",
        "date": date,
        "count": len(filtered),
        "content": filtered
    }


@app.delete("/api/data")
def clear_data():
    save_data({"content": []})
    return {
        "status": "success",
        "message": "Bütün data silindi"
    }
