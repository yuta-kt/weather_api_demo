from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random
from typing import List, Optional

app = FastAPI(
    title="Weather API",
    description="Simple Weather API for learning purposes",
    version="1.0.0"
)

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データモデルの定義
class WeatherData(BaseModel):
    timestamp: datetime
    temperature: float
    humidity: float
    condition: str
    windSpeed: float
    location: str

class City(BaseModel):
    id: str
    name: str

# サンプルデータ
weather_data = {
    "tokyo": {
        "id": "tokyo",
        "name": "東京",
        "base_data": {
            "temperature": 25.6,
            "humidity": 65,
            "condition": "Sunny",
            "windSpeed": 3.2,
            "location": "Tokyo"
        }
    },
    "osaka": {
        "id": "osaka",
        "name": "大阪",
        "base_data": {
            "temperature": 26.2,
            "humidity": 70,
            "condition": "Cloudy",
            "windSpeed": 2.8,
            "location": "Osaka"
        }
    }
}

def generate_weather_data(base_data: dict) -> WeatherData:
    """ベースデータを元に、若干のランダムな変動を加えた天気データを生成"""
    return WeatherData(
        timestamp=datetime.now(),
        temperature=base_data["temperature"] + (random.random() * 2 - 1),  # ±1度の変動
        humidity=min(100, max(0, base_data["humidity"] + (random.random() * 10 - 5))),  # ±5%の変動
        condition=base_data["condition"],
        windSpeed=max(0, base_data["windSpeed"] + (random.random() - 0.5)),  # ±0.5m/sの変動
        location=base_data["location"]
    )

@app.get("/api/weather/{city_id}", response_model=WeatherData)
async def get_weather(city_id: str):
    """特定の都市の現在の天気データを取得"""
    if city_id not in weather_data:
        raise HTTPException(status_code=404, detail="City not found")
    
    return generate_weather_data(weather_data[city_id]["base_data"])

@app.get("/api/cities", response_model=List[City])
async def get_cities():
    """利用可能な都市の一覧を取得"""
    return [
        City(id=city["id"], name=city["name"])
        for city in weather_data.values()
    ]

# 開発用サーバー起動設定
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
