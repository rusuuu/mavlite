import csv, time, sys
from pymavlink import mavutil

nume = sys.argv[1] if len(sys.argv) > 1 else 'ground_truth.csv'

conn = mavutil.mavlink_connection('udp:127.0.0.1:14551')
conn.wait_heartbeat()
print(f"Conectat. Scriu in {nume}. Ctrl+C pentru stop.")

with open(nume, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['t', 'lat', 'lon', 'alt', 'vx', 'vy', 'vz', 'hdg'])
    t0 = time.time()
    try:
        while True:
            m = conn.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            w.writerow([
                round(time.time() - t0, 3),
                m.lat / 1e7,
                m.lon / 1e7,
                m.relative_alt / 1000.0,
                m.vx / 100.0,
                m.vy / 100.0,
                m.vz / 100.0,
                m.hdg / 100.0,
            ])
            f.flush()
    except KeyboardInterrupt:
        print("Oprit.")
