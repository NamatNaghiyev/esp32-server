from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime

app = FastAPI()

DATA_FILE = "sensor_data.json"


class SensorData(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil: Optional[int] = None
    pressure: Optional[float] = None
    gasResistance: Optional[float] = None
    bme_temperature: Optional[float] = None
    bme_humidity: Optional[float] = None
    timestamp: Optional[str] = None


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@app.get("/")
def home():
    return {"message": "ESP32 server is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/data")
def receive_data(sensor_data: SensorData):
    all_data = load_data()

    record = sensor_data.dict()

    if not record.get("timestamp"):
        record["timestamp"] = datetime.now().isoformat()

    all_data.append(record)
    save_data(all_data)

    return {
        "message": "Data received successfully",
        "total_records": len(all_data),
        "saved_data": record
    }


@app.get("/api/data")
def get_all_data():
    all_data = load_data()
    return {
        "count": len(all_data),
        "data": all_data
    }


@app.get("/download/json")
def download_json():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="JSON file not found")

    return FileResponse(
        path=DATA_FILE,
        media_type="application/json",
        filename="sensor_data.json"
    )


@app.delete("/api/data")
def clear_data():
    save_data([])
    return {"message": "All data cleared"}
