from pymavlink import mavutil

conn = mavutil.mavlink_connection('udp:127.0.0.1:14551')
conn.wait_heartbeat()
print("Conectat la sistem %u" % conn.target_system)

while True:
    msg = conn.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    lat = msg.lat / 1e7
    lon = msg.lon / 1e7
    alt = msg.relative_alt / 1000.0
    print(f"lat={lat:.7f} lon={lon:.7f} alt={alt:.2f}m")
