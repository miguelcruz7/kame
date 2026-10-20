"""Create two short Cockpit mission drafts around Kame's SITL start point."""

import json
import math
import uuid
from pathlib import Path


ORIGIN = (43.340080, -8.384526)
EARTH_RADIUS_M = 6_378_137.0
DESTINATION = Path(__file__).parent / "misiones"


def offset(east_m: float, north_m: float) -> list[float]:
    latitude, longitude = ORIGIN
    lat = latitude + math.degrees(north_m / EARTH_RADIUS_M)
    lon = longitude + math.degrees(east_m / (EARTH_RADIUS_M * math.cos(math.radians(latitude))))
    return [round(lat, 8), round(lon, 8)]


def waypoint(mission: str, index: int, east_m: float, north_m: float) -> dict:
    return {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"kame-sitl:{mission}:{index}")),
        "coordinates": offset(east_m, north_m),
        "altitude": 0,
        "altitudeReferenceType": "Relative to home",
        "commands": [
            {
                "type": "MAVLINK_NAV_COMMAND",
                "command": 16,
                "param1": 0,
                "param2": 5,
                "param3": 0,
                "param4": 999,
            }
        ],
    }


def save_mission(filename: str, points: list[tuple[float, float]]) -> None:
    mission = {
        "version": 0,
        "settings": {
            "mapCenter": list(ORIGIN),
            "zoom": 18,
            "currentWaypointAltitude": 0,
            "currentWaypointAltitudeRefType": "Relative to home",
            "defaultCruiseSpeed": 1.2,
        },
        "waypoints": [waypoint(filename, index, *point) for index, point in enumerate(points, start=1)],
        "surveys": [],
    }
    DESTINATION.mkdir(parents=True, exist_ok=True)
    (DESTINATION / filename).write_text(json.dumps(mission, indent=2) + "\n", encoding="utf-8")


save_mission("01_ida_y_vuelta.cmp", [(-40, 0), (-80, 0), (0, 0)])
save_mission("02_triangulo.cmp", [(-40, 0), (-40, -40), (0, 0)])
