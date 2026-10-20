#!/usr/bin/env python3
"""Keep YOLO as the sole BlueOS/Cockpit video source on the Kame vehicle."""

import copy
import datetime
import json
import pathlib
import urllib.parse
import urllib.request
import uuid


BASE = "http://127.0.0.1"
MCM = "http://127.0.0.1:6020"
YOLO_NAME = "YOLO26n Person + Boat"
RAW_NAME = "Waveshare IMX462 1080p20"
PROFILE_KEY = "cockpit-saved-profiles-v8"
MAPPING_KEY = "cockpit-streams-correspondency"
ALLOWED_ICE_IPS_KEY = "cockpit-allowed-stream-ips"
AUTO_ICE_IP_FETCH_KEY = "cockpit-enable-auto-ice-ip-fetch"


def request_json(url, method="GET", payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if body is not None else {}
    with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers, method=method), timeout=15) as response:
        content = response.read()
        return json.loads(content) if content else None


def video_widgets(view):
    return [widget for widget in view.get("widgets", []) if widget.get("component") == "VideoPlayer"]


def update_profiles(profiles):
    profiles = copy.deepcopy(profiles)
    changes = []
    for profile in profiles:
        for view in profile.get("views", []):
            widgets = view.setdefault("widgets", [])
            videos = video_widgets(view)
            if videos:
                # Keep the larger existing player and preserve its geometry/options.
                keeper = max(videos, key=lambda w: w.get("size", {}).get("width", 0) * w.get("size", {}).get("height", 0))
                view["widgets"] = [w for w in widgets if w.get("component") != "VideoPlayer" or w is keeper]
            else:
                # A small overlay keeps the map and other widgets available.
                keeper = {
                    "hash": str(uuid.uuid4()),
                    "name": "Video player",
                    "component": "VideoPlayer",
                    "position": {"x": 0.665, "y": 0.59},
                    "size": {"width": 0.335, "height": 0.38},
                    "options": {"videoFitStyle": "contain"},
                }
                widgets.insert(0, keeper)
            keeper.setdefault("options", {})["internalStreamName"] = "Stream 1"
            changes.append((profile.get("name"), view.get("name"), len(videos)))
    return profiles, changes


def main():
    streams = request_json(f"{MCM}/streams")
    names = [stream["video_and_stream"]["name"] for stream in streams]
    if YOLO_NAME not in names or any(name not in (YOLO_NAME, RAW_NAME) for name in names):
        raise RuntimeError(f"Unexpected BlueOS video sources: {names}")

    settings = request_json(f"{BASE}/bag/v1.0/get/cockpit/settings")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = pathlib.Path.home() / f"cockpit-video-before-yolo-only-{stamp}.json"
    backup.write_text(json.dumps({"settings": settings, "streams": streams}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Backup: {backup}")

    mapping = [{"name": "Stream 1", "externalId": YOLO_NAME}]
    for username, user_settings in settings.items():
        profiles = user_settings.get(PROFILE_KEY)
        if not isinstance(profiles, list):
            continue
        updated, changes = update_profiles(profiles)
        user = urllib.parse.quote(username, safe="")
        prefix = f"{BASE}/bag/v1.0/set/cockpit/settings/{user}"
        request_json(f"{prefix}/{PROFILE_KEY}", "POST", updated)
        request_json(f"{prefix}/{MAPPING_KEY}", "POST", mapping)
        # An empty whitelist accepts every ICE candidate. Cockpit's automatic
        # preference for wired addresses can otherwise pin video to Ethernet.
        request_json(f"{prefix}/{ALLOWED_ICE_IPS_KEY}", "POST", [])
        request_json(f"{prefix}/{AUTO_ICE_IP_FETCH_KEY}", "POST", False)
        print(f"User {username}: {changes}")

    if RAW_NAME in names:
        url = f"{MCM}/delete_stream?{urllib.parse.urlencode({'name': RAW_NAME})}"
        request_json(url, "DELETE")

    final_streams = request_json(f"{MCM}/streams")
    final_names = [stream["video_and_stream"]["name"] for stream in final_streams]
    if final_names != [YOLO_NAME]:
        raise RuntimeError(f"BlueOS video source mismatch after update: {final_names}")
    print(f"BlueOS now advertises only: {final_names[0]}")


if __name__ == "__main__":
    main()
