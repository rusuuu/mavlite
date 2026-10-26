import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math, random
import lpp

R = 6378137.0
lat_ref = -35.363262

# pasul de cuantizare in metri, pentru fiecare format
pas_lat_std = math.radians(1e-4) * R
pas_lon_std = math.radians(1e-4) * R * math.cos(math.radians(lat_ref))
print(f"LPP standard: pas lat = {pas_lat_std:.2f} m, pas lon = {pas_lon_std:.2f} m")

pas_lat_cst = math.radians(1e-6) * R
print(f"LPP custom:   pas lat = {pas_lat_cst:.4f} m")
print(f"delta:        pas = 0.10 m (unitate 0.1 m)")

# eroare medie teoretica pentru rotunjire uniforma: pas/4 pe axa,
# iar pe doua axe ~0.38*pas (media distantei euclidiene)
print(f"\nEroare medie teoretica (standard): ~{0.38*pas_lat_std:.2f} m")
print(f"Eroare maxima teoretica (standard): ~{math.hypot(pas_lat_std, pas_lon_std)/2:.2f} m")

# verificare empirica pe puncte aleatoare
erori = []
for _ in range(10000):
    lat = lat_ref + random.uniform(-0.01, 0.01)
    lon = 149.165 + random.uniform(-0.01, 0.01)
    p = lpp.encode_lpp_standard(lat, lon, 20.0)
    lat2, lon2, _ = lpp.decode_lpp_standard(p)
    erori.append(lpp.distanta(lat, lon, lat2, lon2))

import statistics
print(f"\nEmpiric pe 10000 puncte aleatoare:")
print(f"  medie = {statistics.mean(erori):.2f} m")
print(f"  max   = {max(erori):.2f} m")

