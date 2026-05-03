"""
地图导航 API
调用高德地图 Web 服务 API 进行路线规划
"""
import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.core.config import settings

router = APIRouter()


@router.get("/route")
async def plan_route(
    origin: str = Query(..., description="起点坐标，格式：经度,纬度"),
    destination: str = Query(..., description="终点坐标，格式：经度,纬度"),
    mode: str = Query("driving", description="出行方式：driving/transit/walking"),
):
    """调用高德地图路线规划 API"""
    
    if not settings.AMAP_API_KEY:
        raise HTTPException(status_code=500, detail="高德地图 API Key 未配置")
    
    url_map = {
        "driving": "https://restapi.amap.com/v3/direction/driving",
        "transit": "https://restapi.amap.com/v3/direction/transit/integrated",
        "walking": "https://restapi.amap.com/v3/direction/walking",
    }
    
    api_url = url_map.get(mode, url_map["driving"])
    
    params = {
        "key": settings.AMAP_API_KEY,
        "origin": origin,
        "destination": destination,
        "extensions": "all",
    }
    
    if mode == "transit":
        params["city"] = "上海"
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(api_url, params=params)
        data = response.json()
    
    if data.get("status") != "1":
        raise HTTPException(status_code=400, detail=data.get("info", "路线规划失败"))
    
    return parse_route_result(data, mode)


def parse_route_result(data: dict, mode: str) -> dict:
    """解析高德API返回结果，提取关键信息"""
    result = {
        "mode": mode,
        "distance": 0,
        "duration": 0,
        "steps": [],
        "polyline": "",
    }
    
    if mode == "driving":
        route = data.get("route", {})
        path = route.get("paths", [{}])[0]
        result["distance"] = int(path.get("distance", 0))
        result["duration"] = int(path.get("duration", 0))
        result["steps"] = [
            {
                "instruction": step.get("instruction", ""),
                "road": step.get("road", ""),
                "distance": int(step.get("distance", 0)),
            }
            for step in path.get("steps", [])
        ]
        polyline_points = []
        for step in path.get("steps", []):
            polyline_points.append(step.get("polyline", ""))
        result["polyline"] = ";".join([p for p in polyline_points if p])
    
    elif mode == "transit":
        route = data.get("route", {})
        transits = route.get("transits", [])
        if transits:
            transit = transits[0]
            result["distance"] = int(transit.get("distance", 0))
            result["duration"] = int(transit.get("duration", 0))
            result["cost"] = transit.get("cost", {})
            result["steps"] = [
                {
                    "type": segment.get("bus", {}).get("buslines", [{}])[0].get("type", ""),
                    "name": segment.get("bus", {}).get("buslines", [{}])[0].get("name", ""),
                    "departure_stop": segment.get("bus", {}).get("buslines", [{}])[0].get("departure_stop", {}).get("name", ""),
                    "arrival_stop": segment.get("bus", {}).get("buslines", [{}])[0].get("arrival_stop", {}).get("name", ""),
                }
                for segment in transit.get("segments", [])
                if segment.get("bus")
            ]
    
    elif mode == "walking":
        route = data.get("route", {})
        path = route.get("paths", [{}])[0]
        result["distance"] = int(path.get("distance", 0))
        result["duration"] = int(path.get("duration", 0))
        result["steps"] = [
            {
                "instruction": step.get("instruction", ""),
                "distance": int(step.get("distance", 0)),
            }
            for step in path.get("steps", [])
        ]
        polyline_points = []
        for step in path.get("steps", []):
            polyline_points.append(step.get("polyline", ""))
        result["polyline"] = ";".join([p for p in polyline_points if p])
    
    return result


@router.get("/geocode")
async def geocode(address: str = Query(..., description="地址文本")):
    """地址转坐标（地理编码）"""
    
    if not settings.AMAP_API_KEY:
        raise HTTPException(status_code=500, detail="高德地图 API Key 未配置")
    
    url = "https://restapi.amap.com/v3/geocode/geo"
    
    params = {
        "key": settings.AMAP_API_KEY,
        "address": address,
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        data = response.json()
    
    if data.get("status") != "1" or not data.get("geocodes"):
        raise HTTPException(status_code=400, detail="地址解析失败")
    
    geocode = data["geocodes"][0]
    return {
        "location": geocode.get("location"),
        "formatted_address": geocode.get("formatted_address"),
        "province": geocode.get("province"),
        "city": geocode.get("city"),
        "district": geocode.get("district"),
    }
