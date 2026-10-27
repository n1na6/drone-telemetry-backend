import time
from mavlink_reader import TelemetryReader

def on_event(event_type, data):
    if event_type == "waypoint":
        print(f"[MISSION] Reached waypoint {data['seq']}")
    elif event_type == "statustext":
        print(f"[STATUS] {data['text']}")
    elif event_type == "disconnected":
        print("[LINK] Connection lost")

reader = TelemetryReader("udpin:0.0.0.0:14560")
reader.subscribe(on_event)
reader.start()

while True:
    print(reader.snapshot())
    time.sleep(1)