from pymavlink import mavutil
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.spray_service.spray_controller import spray_on, spray_off

print("Connecting...")

master = mavutil.mavlink_connection('udpin:0.0.0.0:14560')

master.wait_heartbeat()

print("Connected")

last_wp = -1
spray_initialized = False

while True:

    msg = master.recv_match(blocking=True, timeout=5)

    if not msg:
        continue

    msg_type = msg.get_type()

    # 🚁 WAYPOINT LOGIC (SAFE)
    if msg_type == "MISSION_CURRENT" and hasattr(msg, "seq"):
        
        
        if not spray_initialized:
            spray_initialized = True
            print("Spray system ready")
        
        if msg.seq != last_wp:
            last_wp = msg.seq

            print(f"[MISSION] WP: {msg.seq}")

            if msg.seq == 10:
                spray_on()
            elif msg.seq == 20:
                spray_off()

        

    # 📍 GPS
    elif msg_type == "GLOBAL_POSITION_INT":

        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.relative_alt / 1000

        print(f"[GPS] LAT={lat:.6f} LON={lon:.6f} ALT={alt:.1f}m")

    # 🔋 BATTERY
    elif msg_type == "SYS_STATUS":

        print(f"[BATTERY] {msg.battery_remaining}%")