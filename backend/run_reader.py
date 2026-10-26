import time
from mavlink_reader import TelemetryReader

# Stub for now. Swap in your real spray_controller later.
def spray_on():
    print(">>> SPRAY ON")

def spray_off():
    print(">>> SPRAY OFF")

def spray_handler(event_type, data):
    if event_type == "waypoint":
        print(f"[MISSION] WP {data['seq']}")
        spray_on() if 10 <= data["seq"] < 20 else spray_off()
    elif event_type == "statustext":
        print(f"[STATUS] {data['text']}")
    elif event_type == "disconnected":
        print("[LINK] lost, failsafe: spray off")
        spray_off()

reader = TelemetryReader("udpin:0.0.0.0:14560")
reader.subscribe(spray_handler)
reader.start()

while True:
    print(reader.snapshot())
    time.sleep(1)
