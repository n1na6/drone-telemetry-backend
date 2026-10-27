import threading
import time
from pymavlink import mavutil


class TelemetryReader:
    def __init__(self, conn="udpin:0.0.0.0:14560"):
        self.conn = conn
        self._lock = threading.Lock()
        self._listeners = []  # callbacks: fn(event_type, data)
        self._last_msg_time = 0.0
        self.state = {
            "connected": False, "mode": None,
            "lat": None, "lon": None, "alt": None,
            "groundspeed": None, "heading": None,
            "battery": None, "waypoint": None,
        }

    def subscribe(self, fn):
        self._listeners.append(fn)

    def snapshot(self):
        with self._lock:
            return dict(self.state)

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _emit(self, event_type, data):
        for fn in self._listeners:
            fn(event_type, data)

    def _update(self, **kw):
        with self._lock:
            self.state.update(kw)

    def _run(self):
        master = mavutil.mavlink_connection(self.conn)
        master.wait_heartbeat()
        self._update(connected=True)
        self._last_msg_time = time.time()

        while True:
            msg = master.recv_match(blocking=True, timeout=1)

            if msg is None:
                if self.state["connected"] and time.time() - self._last_msg_time > 5:
                    self._update(connected=False)
                    self._emit("disconnected", {})
                continue

            self._last_msg_time = time.time()
            if not self.state["connected"]:
                self._update(connected=True)

            t = msg.get_type()
            if t == "HEARTBEAT":
                self._update(mode=master.flightmode)
            elif t == "GLOBAL_POSITION_INT":
                self._update(lat=msg.lat / 1e7, lon=msg.lon / 1e7,
                             alt=msg.relative_alt / 1000)
            elif t == "VFR_HUD":
                self._update(groundspeed=msg.groundspeed, heading=msg.heading)
            elif t == "SYS_STATUS":
                b = msg.battery_remaining
                self._update(battery=None if b < 0 else b)
            elif t == "MISSION_CURRENT":
                if msg.seq != self.state["waypoint"]:
                    self._update(waypoint=msg.seq)
                    self._emit("waypoint", {"seq": msg.seq})
            elif t == "STATUSTEXT":
                self._emit("statustext", {"text": msg.text})
