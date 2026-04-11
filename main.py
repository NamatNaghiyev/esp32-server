from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime

app = FastAPI()

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


class SensorData(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil: Optional[int] = None
    pressure: Optional[float] = None
    gasResistance: Optional[float] = None
    bme_temperature: Optional[float] = None
    bme_humidity: Optional[float] = None
    timestamp: Optional[str] = None


def get_date_str(timestamp: Optional[str] = None) -> str:
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            pass
    return datetime.now().strftime("%Y-%m-%d")


def get_file_path(date_str: str) -> str:
    return os.path.join(DATA_DIR, f"{date_str}.json")


def load_data_by_date(date_str: str):
    file_path = get_file_path(date_str)
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_data_by_date(date_str: str, data):
    file_path = get_file_path(date_str)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def list_available_dates():
    files = []
    for name in os.listdir(DATA_DIR):
        if name.endswith(".json"):
            files.append(name.replace(".json", ""))
    files.sort()
    return files


@app.get("/")
def home():
    return {"message": "ESP32 server is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/data")
def receive_data(sensor_data: SensorData):
    record = sensor_data.model_dump()

    if not record.get("timestamp"):
        record["timestamp"] = datetime.now().isoformat()

    date_str = get_date_str(record["timestamp"])
    all_data = load_data_by_date(date_str)
    all_data.append(record)
    save_data_by_date(date_str, all_data)

    return {
        "message": "Data received successfully",
        "date": date_str,
        "total_records_today": len(all_data),
        "saved_data": record
    }


@app.get("/api/data")
def get_data(date: Optional[str] = Query(default=None)):
    if date:
        data = load_data_by_date(date)
        return {
            "date": date,
            "count": len(data),
            "data": data
        }

    result = {}
    total_count = 0
    for date_str in list_available_dates():
        day_data = load_data_by_date(date_str)
        result[date_str] = {
            "count": len(day_data),
            "data": day_data
        }
        total_count += len(day_data)

    return {
        "total_dates": len(result),
        "total_records": total_count,
        "dates": result
    }


@app.get("/api/dates")
def get_dates():
    dates = list_available_dates()
    return {
        "count": len(dates),
        "dates": dates
    }


@app.get("/download/json")
def download_json(date: str = Query(..., description="Format: YYYY-MM-DD")):
    file_path = get_file_path(date)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="JSON file not found for this date")

    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=f"{date}.json"
    )


@app.get("/clear")
def clear_data_browser(date: Optional[str] = Query(default=None)):
    if date:
        file_path = get_file_path(date)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": f"{date} data cleared"}
        return {"message": f"{date} file not found"}

    dates = list_available_dates()
    for date_str in dates:
        file_path = get_file_path(date_str)
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"message": "All dated data cleared"}


@app.delete("/api/data")
def clear_data(date: Optional[str] = Query(default=None)):
    if date:
        file_path = get_file_path(date)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": f"{date} data cleared"}
        return {"message": f"{date} file not found"}

    dates = list_available_dates()
    for date_str in dates:
        file_path = get_file_path(date_str)
        if os.path.exists(file_path):
            os.remove(file_path)

    return {"message": "All dated data cleared"}
