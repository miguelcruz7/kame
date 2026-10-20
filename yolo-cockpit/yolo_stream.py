#!/usr/bin/env python3
"""Read the existing camera RTSP stream, annotate person/boat, publish a new RTSP feed."""

import logging
import os
import queue
import threading
import time
from fractions import Fraction

import av
import cv2
import torch
from ultralytics import YOLO


SOURCE = os.getenv("YOLO_SOURCE", "rtsp://127.0.0.1:8554/cam")
DESTINATION = os.getenv("YOLO_DESTINATION", "rtsp://127.0.0.1:8556/yolo")
MODEL = os.getenv("YOLO_MODEL", "/home/pi/kame-yolo-offline/model-fp16-320/yolo26n_ncnn_model")
INFER_SIZE = int(os.getenv("YOLO_IMGSZ", "320"))
OUTPUT_FPS = int(os.getenv("YOLO_OUTPUT_FPS", "8"))
INFER_FPS = float(os.getenv("YOLO_INFER_FPS", "8"))
NCNN_THREADS = int(os.getenv("YOLO_NCNN_THREADS", "1"))
OUTPUT_WIDTH = int(os.getenv("YOLO_OUTPUT_WIDTH", "960"))
OUTPUT_HEIGHT = int(os.getenv("YOLO_OUTPUT_HEIGHT", "540"))
CONFIDENCE = float(os.getenv("YOLO_CONFIDENCE", "0.15"))
HOLD_FRAMES = int(os.getenv("YOLO_HOLD_FRAMES", "2"))
STALE_VIEW_SECONDS = 0.75
WATCHDOG_SECONDS = 4.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("kame-yolo")
torch.set_num_threads(1)

# Keep only the newest decoded frame so slower inference never builds a backlog.
latest_frame = queue.Queue(maxsize=1)
annotated = queue.Queue(maxsize=1)
stopping = threading.Event()
health_lock = threading.Lock()
health = {"started": time.monotonic(), "camera": None, "inference": None, "publisher": None}


def note_health(name):
    with health_lock:
        health[name] = time.monotonic()


def watchdog():
    """Let systemd restart us if a PyAV read or write never returns."""
    while not stopping.wait(0.5):
        now = time.monotonic()
        with health_lock:
            state = health.copy()
        for name in ("camera", "inference", "publisher"):
            last = state[name]
            if last is not None and now - last > WATCHDOG_SECONDS:
                log.error("%s stalled for %.1f seconds; restarting detector", name, now - last)
                os._exit(1)
        if state["camera"] is None and now - state["started"] > 30:
            log.error("No camera frames after 30 seconds; restarting detector")
            os._exit(1)
        if state["camera"] is not None and state["inference"] is None and now - state["started"] > 30:
            log.error("No inference after 30 seconds; restarting detector")
            os._exit(1)


def replace_item(q, item):
    try:
        q.put_nowait(item)
    except queue.Full:
        try:
            q.get_nowait()
        except queue.Empty:
            pass
        q.put_nowait(item)


def decode_source():
    while not stopping.is_set():
        try:
            log.info("Connecting to camera stream %s", SOURCE)
            with av.open(SOURCE, options={"rtsp_transport": "tcp"}, timeout=(3.0, 3.0)) as inp:
                stream = inp.streams.video[0]
                log.info("Camera input: %sx%s at reported %s fps", stream.width, stream.height, stream.average_rate)
                first_frame_at = None
                first_media_time = None
                best_media_lag = 0.0
                last_rate_log = time.monotonic()
                decoded = 0
                for frame in inp.decode(stream):
                    if stopping.is_set():
                        break
                    image = frame.to_ndarray(format="bgr24")
                    now = time.monotonic()
                    media_time = float(frame.pts * frame.time_base) if frame.pts is not None else None
                    if first_frame_at is None:
                        first_frame_at, first_media_time = now, media_time
                    note_health("camera")
                    replace_item(latest_frame, (now, image))
                    media_lag = ((now - first_frame_at) - (media_time - first_media_time)
                                 if media_time is not None and first_media_time is not None else float("nan"))
                    if media_time is not None:
                        best_media_lag = min(best_media_lag, media_lag)
                        if now - first_frame_at > 10 and media_lag - best_media_lag > 1.5:
                            log.warning("Camera buffer fell %.2f s behind; reconnecting",
                                        media_lag - best_media_lag)
                            break
                    decoded += 1
                    if now - last_rate_log >= 15:
                        log.info("Camera decode rate: %.2f fps; source backlog growth: %.2f s",
                                 decoded / (now - last_rate_log), media_lag)
                        decoded, last_rate_log = 0, now
                if not stopping.is_set():
                    log.warning("Camera stream ended; reconnecting")
        except Exception:
            log.exception("Camera read failed; reconnecting")
        stopping.wait(1)


def overlap(a, b):
    """Intersection over union for two pixel-space boxes."""
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    intersection = max(0, right - left) * max(0, bottom - top)
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    union = area_a + area_b - intersection
    return intersection / union if union else 0.0


def update_tracks(tracks, detections):
    """Retain a missing box for at most two subsequent inference frames."""
    matched = set()
    updated = []
    for detection in detections:
        candidates = ((overlap(detection["box"], track["box"]), index)
                      for index, track in enumerate(tracks)
                      if index not in matched and track["cls"] == detection["cls"])
        score, index = max(candidates, default=(0.0, None))
        if score >= 0.3:
            matched.add(index)
        updated.append({**detection, "misses": 0})
    for index, track in enumerate(tracks):
        if index not in matched and track["misses"] < HOLD_FRAMES:
            updated.append({**track, "misses": track["misses"] + 1})
    return updated


def draw_tracks(image, tracks):
    height, width = image.shape[:2]
    view = cv2.resize(image, (OUTPUT_WIDTH, OUTPUT_HEIGHT), interpolation=cv2.INTER_AREA)
    scale_x, scale_y = OUTPUT_WIDTH / width, OUTPUT_HEIGHT / height
    for track in tracks:
        x1, y1, x2, y2 = track["box"]
        x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
        y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
        x1, x2 = max(0, x1), min(OUTPUT_WIDTH - 1, x2)
        y1, y2 = max(0, y1), min(OUTPUT_HEIGHT - 1, y2)
        held = track["misses"] > 0
        color = (150, 150, 150) if held else ((40, 220, 40) if track["cls"] == 0 else (255, 180, 30))
        name = "person" if track["cls"] == 0 else "boat"
        label = f"{name} {track['conf']:.2f}" + (" hold" if held else "")
        cv2.rectangle(view, (x1, y1), (x2, y2), color, 2)
        text_y = max(18, y1 - 6)
        cv2.putText(view, label, (x1, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return view


def stale_frame():
    import numpy as np
    view = np.zeros((OUTPUT_HEIGHT, OUTPUT_WIDTH, 3), dtype=np.uint8)
    cv2.putText(view, "VIDEO SIN DATOS - RECONECTANDO", (32, OUTPUT_HEIGHT // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (40, 40, 255), 2)
    return view


def infer(model):
    last_log = time.monotonic()
    count = 0
    tracks = []
    while not stopping.is_set():
        try:
            captured_at, image = latest_frame.get(timeout=1)
        except queue.Empty:
            continue
        if time.monotonic() - captured_at > 1:
            continue
        try:
            inference_start = time.monotonic()
            result = model.predict(image, imgsz=INFER_SIZE, classes=[0, 8], conf=CONFIDENCE, verbose=False)[0]
            detections = [{"box": tuple(float(value) for value in box.xyxy[0].tolist()),
                           "cls": int(box.cls.item()), "conf": float(box.conf.item())}
                          for box in result.boxes]
            tracks = update_tracks(tracks, detections)
            view = draw_tracks(image, tracks)
            note_health("inference")
            replace_item(annotated, (time.monotonic(), view))
            count += 1
            now = time.monotonic()
            if now - last_log >= 15:
                log.info("Inference rate: %.2f fps; last detections: %s", count / (now - last_log),
                         [(result.names[int(b.cls)], round(float(b.conf), 2)) for b in result.boxes])
                count, last_log = 0, now
            stopping.wait(max(0, 1 / INFER_FPS - (time.monotonic() - inference_start)))
        except Exception:
            log.exception("Inference failed")


def main():
    # Ultralytics creates the NCNN Net internally; configure its OpenMP thread
    # count before loading weights so the runtime does not start a large pool.
    from pathlib import Path
    from ultralytics.nn.backends.ncnn import NCNNBackend

    def load_limited_ncnn(self, weight):
        import ncnn
        self.pyncnn = ncnn
        self.net = ncnn.Net()
        self.net.opt.use_vulkan_compute = False
        self.net.opt.num_threads = NCNN_THREADS
        w = Path(weight)
        if not w.is_file():
            w = next(w.glob("*.param"))
        self.net.load_param(str(w))
        self.net.load_model(str(w.with_suffix(".bin")))
        self.apply_metadata(self.read_metadata(w))

    NCNNBackend.load_model = load_limited_ncnn
    log.info("Loading NCNN model %s", MODEL)
    model = YOLO(MODEL)
    threading.Thread(target=watchdog, name="stream-watchdog", daemon=True).start()
    threading.Thread(target=decode_source, name="rtsp-reader", daemon=True).start()
    threading.Thread(target=infer, args=(model,), name="yolo-infer", daemon=True).start()

    # Publish at a modest fixed cadence, repeating the latest annotation between inferences.
    while not stopping.is_set():
        try:
            image_at, image = annotated.get(timeout=30)
            break
        except queue.Empty:
            log.warning("Waiting for a decoded/annotated camera frame")
    else:
        return

    log.info("Publishing annotated video to %s at %s fps", DESTINATION, OUTPUT_FPS)
    warning_frame = stale_frame()
    while not stopping.is_set():
        output = None
        stream = None
        try:
            note_health("publisher")
            output = av.open(DESTINATION, mode="w", format="rtsp",
                             options={"rtsp_transport": "tcp"}, timeout=(3.0, 3.0))
            stream = output.add_stream("libx264", rate=OUTPUT_FPS)
            stream.width = OUTPUT_WIDTH
            stream.height = OUTPUT_HEIGHT
            stream.pix_fmt = "yuv420p"
            stream.codec_context.gop_size = OUTPUT_FPS
            stream.bit_rate = 1_200_000
            stream.options = {"preset": "ultrafast", "tune": "zerolatency", "profile": "baseline",
                              "x264-params": f"keyint={OUTPUT_FPS}:min-keyint={OUTPUT_FPS}:scenecut=0:repeat-headers=1"}
            log.info("RTSP publisher connected")
            pts = 0
            published = 0
            last_publish_log = time.monotonic()
            frame_image = image
            frame_at = image_at
            while not stopping.is_set():
                frame_start = time.monotonic()
                try:
                    frame_at, frame_image = annotated.get_nowait()
                except queue.Empty:
                    pass
                visible = frame_image if frame_start - frame_at <= STALE_VIEW_SECONDS else warning_frame
                frame = av.VideoFrame.from_ndarray(visible, format="bgr24")
                frame.pts = pts
                frame.time_base = Fraction(1, OUTPUT_FPS)
                pts += 1
                for packet in stream.encode(frame):
                    output.mux(packet)
                note_health("publisher")
                published += 1
                now = time.monotonic()
                if now - last_publish_log >= 15:
                    log.info("Publish rate: %.2f fps; latest annotation age: %.2f s",
                             published / (now - last_publish_log), now - frame_at)
                    published, last_publish_log = 0, now
                # Budget encoding and muxing time into the frame interval so
                # the actual cadence stays close to OUTPUT_FPS.
                time.sleep(max(0, 1 / OUTPUT_FPS - (time.monotonic() - frame_start)))
        except Exception:
            log.exception("RTSP publishing failed; retrying in 3 seconds")
            stopping.wait(3)
        finally:
            try:
                if output is not None:
                    if stream is not None:
                        for packet in stream.encode(None):
                            output.mux(packet)
                    output.close()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stopping.set()
