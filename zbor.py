import os
RADACINA = os.path.dirname(os.path.abspath(__file__))
DATE = os.path.join(RADACINA, 'date')
os.makedirs(DATE, exist_ok=True)

import csv, time, sys, math
from pymavlink import mavutil

SCENARIU = sys.argv[1] if len(sys.argv) > 1 else 'linie'
ALT = 20.0
TOLERANTA = 3.0      # metri
TIMP_MIN_SEGMENT = 3.0   # secunde minime per segment

TRASEE = {
    'linie':  [(200,0)],
    'patrat': [(100,0), (100,100), (0,100), (0,0)],
    'zigzag': [(50,40), (100,-40), (150,40), (200,-40)],
    'hover':  [],
}

puncte = TRASEE[SCENARIU]

conn = mavutil.mavlink_connection('udp:127.0.0.1:14551')
conn.wait_heartbeat()
print(f"Conectat. Scenariu: {SCENARIU}")

m = conn.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
if m.relative_alt / 1000.0 < 5:
    print("EROARE: drona nu e in aer.")
    print("Decoleaza intai: mode guided / arm throttle / takeoff 20")
    sys.exit(1)

# cer explicit ambele mesaje la 5 Hz
for msg_id in (mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
               mavutil.mavlink.MAVLINK_MSG_ID_LOCAL_POSITION_NED):
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        0, msg_id, 200000, 0, 0, 0, 0, 0)   # 200000 us = 5 Hz
time.sleep(1)

def trimite_tinta(nord, est, alt):
    conn.mav.set_position_target_local_ned_send(
        0, conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b110111111000,
        nord, est, -alt,
        0,0,0, 0,0,0, 0,0)

f = open(os.path.join(DATE, f'{SCENARIU}.csv'), 'w', newline='')
w = csv.writer(f)
w.writerow(['t','lat','lon','alt','vx','vy','vz','hdg','n','e'])
t0 = time.time()

stare = {'lat':0,'lon':0,'alt':0,'vx':0,'vy':0,'vz':0,'hdg':0,
         'n':0.0,'e':0.0,'n_proaspat':False}

def citeste_si_logheaza():
    """Citeste un mesaj si scrie un rand. Returneaza True daca pozitia locala e noua."""
    msg = conn.recv_match(type=['GLOBAL_POSITION_INT','LOCAL_POSITION_NED'],
                          blocking=True, timeout=2)
    if msg is None:
        return False
    nou = False
    if msg.get_type() == 'GLOBAL_POSITION_INT':
        stare['lat'] = msg.lat/1e7
        stare['lon'] = msg.lon/1e7
        stare['alt'] = msg.relative_alt/1000.0
        stare['vx'] = msg.vx/100.0
        stare['vy'] = msg.vy/100.0
        stare['vz'] = msg.vz/100.0
        stare['hdg'] = msg.hdg/100.0
    else:
        stare['n'] = msg.x
        stare['e'] = msg.y
        nou = True

    if stare['lat'] == 0:
        return nou

    w.writerow([round(time.time()-t0,3), stare['lat'], stare['lon'],
                stare['alt'], stare['vx'], stare['vy'], stare['vz'],
                stare['hdg'], round(stare['n'],2), round(stare['e'],2)])
    f.flush()
    return nou

for i, (n, e) in enumerate(puncte):
    print(f"-> punct {i+1}/{len(puncte)}: nord={n} est={e}")
    trimite_tinta(n, e, ALT)
    t_start = time.time()
    while True:
        pozitie_noua = citeste_si_logheaza()
        scurs = time.time() - t_start
        if pozitie_noua and scurs > TIMP_MIN_SEGMENT:
            dist = math.hypot(n - stare['n'], e - stare['e'])
            if dist < TOLERANTA:
                print(f"   ajuns (dist={dist:.1f}m, {scurs:.0f}s)")
                break
        if scurs > 180:
            print("   timeout")
            break

durata = 60 if SCENARIU == 'hover' else 5
print(f"hover {durata}s")
t_h = time.time()
while time.time() - t_h < durata:
    citeste_si_logheaza()

f.close()
print(f"Gata. Salvat in date/{SCENARIU}.csv")
