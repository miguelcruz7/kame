#!/usr/bin/env python3
"""Read-only estimate of /cam to /yolo lag from matching camera images."""

import argparse
import threading
import time

import av
import cv2
import numpy as np


def capture(url, seconds, frames, errors):
    try:
        with av.open(
            url,
            options={"rtsp_transport": "tcp", "fflags": "nobuffer", "flags": "low_delay"},
            timeout=(3.0, 3.0),
        ) as stream:
            video = stream.streams.video[0]
            start = time.monotonic()
            for frame in stream.decode(video):
                arrival = time.monotonic()
                rgb = frame.to_ndarray(format="bgr24")
                small = cv2.cvtColor(cv2.resize(rgb, (160, 90)), cv2.COLOR_BGR2GRAY)
                frames.append((arrival, small))
                if arrival - start >= seconds:
                    break
    except Exception as exc:
        errors.append(f"{url}: {exc}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=10)
    args = parser.parse_args()
    streams = {
        "cam": "rtsp://127.0.0.1:8554/cam",
        "yolo": "rtsp://127.0.0.1:8556/yolo",
    }
    images = {name: [] for name in streams}
    errors = []
    workers = [threading.Thread(target=capture, args=(url, args.seconds, images[name], errors))
               for name, url in streams.items()]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()
    for name, frames in images.items():
        duration = frames[-1][0] - frames[0][0] if len(frames) > 1 else 0
        print(f"{name}: {len(frames)} frames / {duration:.2f} s = {len(frames) / duration if duration else 0:.2f} fps")
    for error in errors:
        print(f"ERROR: {error}")
    if not images["cam"] or not images["yolo"]:
        return

    # Skip the startup edge so every YOLO frame has a useful camera search window.
    matches = []
    cam = images["cam"]
    for y_time, y_frame in images["yolo"]:
        candidates = [(float(np.mean(cv2.absdiff(y_frame, c_frame))), c_time)
                      for c_time, c_frame in cam if abs(y_time - c_time) <= 6]
        if candidates:
            error, c_time = min(candidates)
            matches.append((y_time - c_time, error))
    if matches:
        lags = np.array([lag for lag, _ in matches])
        errors = np.array([error for _, error in matches])
        print(f"Matched {len(matches)} frames; lag yolo-minus-cam arrival: "
              f"median={np.median(lags):.2f} s, p10={np.percentile(lags, 10):.2f} s, "
              f"p90={np.percentile(lags, 90):.2f} s; image error median={np.median(errors):.2f}")
        print("First matches:", [(round(lag, 2), round(error, 2)) for lag, error in matches[:10]])
        print("Last matches:", [(round(lag, 2), round(error, 2)) for lag, error in matches[-10:]])


if __name__ == "__main__":
    main()
