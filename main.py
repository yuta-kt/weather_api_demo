from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random
from typing import List, Optional

# 地方ごとのデータをインポート
from data.hokkaido import hokkaido_cities
from data.tohoku import tohoku_cities
from data.kanto import kanto_cities
from data.chubu import chubu_cities
from data.kansai import kansai_cities
from data.chugoku import chugoku_cities
from data.shikoku import shikoku_cities
from data.kyushu import kyushu_cities

app = FastAPI(
    title="Japan Weather API",
    description="Weather API for all prefectural capitals in Japan",
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

# 天気の種類
weather_conditions = [
    "Sunny", "Mostly Sunny", "Partly Cloudy", "Cloudy",
    "Rainy", "Heavy Rain", "Thunder", "Snowy",
    "Foggy", "Light Rain", "Light Snow"
]

# 地域ごとの基本気温調整値（夏場を想定）
region_temp_adjustments = {
    "hokkaido": -8.0,    # 北海道
    "tohoku": -4.0,      # 東北
    "kanto": 0.0,        # 関東（基準）
    "chubu": -1.0,       # 中部
    "kansai": 0.5,       # 関西
    "chugoku": 0.0,      # 中国
    "shikoku": 1.0,      # 四国
    "kyushu": 2.0,       # 九州
    "okinawa": 4.0       # 沖縄
}

# 全国の天気データを結合
weather_data = {
    **hokkaido_cities,
    **tohoku_cities,
    **kanto_cities,
    **chubu_cities,
    **kansai_cities,
    **chugoku_cities,
    **shikoku_cities,
    **kyushu_cities
}

def apply_regional_adjustments():
    """地域ごとの気温調整を適用"""
    for city_id, city_data in weather_data.items():
        region = get_region_for_city(city_id)
        if region in region_temp_adjustments:
            city_data["base_data"]["temperature"] += region_temp_adjustments[region]

def get_region_for_city(city_id: str) -> str:
    """都市IDから地域を判定"""
    region_maps = {
        tuple(hokkaido_cities.keys()): "hokkaido",
        tuple(tohoku_cities.keys()): "tohoku",
        tuple(kanto_cities.keys()): "kanto",
        tuple(chubu_cities.keys()): "chubu",
        tuple(kansai_cities.keys()): "kansai",
        tuple(chugoku_cities.keys()): "chugoku",
        tuple(shikoku_cities.keys()): "shikoku",
    }
    
    # 沖縄（那覇）は特別扱い
    if city_id == "naha":
        return "okinawa"
    
    # その他の九州地域
    if city_id in kyushu_cities:
        return "kyushu"
    
    # その他の地域
    for cities, region in region_maps.items():
        if city_id in cities:
            return region
    
    return "kanto"  # デフォルト値

def generate_weather_data(base_data: dict) -> WeatherData:
    """ベースデータを元に、若干のランダムな変動を加えた天気データを生成"""
    # 10%の確率で天気が変化
    current_condition = base_data["condition"]
    if random.random() < 0.1:
        current_condition = random.choice(weather_conditions)

    return WeatherData(
        timestamp=datetime.now(),
        temperature=base_data["temperature"] + (random.random() * 2 - 1),  # ±1度の変動
        humidity=min(100, max(0, base_data["humidity"] + (random.random() * 10 - 5))),  # ±5%の変動
        condition=current_condition,
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

# 起動時に地域調整を適用
apply_regional_adjustments()

# 開発用サーバー起動設定
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)