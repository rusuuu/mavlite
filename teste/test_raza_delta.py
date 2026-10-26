import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lpp

lat_ref, lon_ref = -35.363262, 149.165237

print(f"{'distanta tinta':>15} {'eroare':>10}")
for d_metri in [100, 1000, 3000, 3276, 3500, 5000, 10000]:
    lat, lon = lpp.ne_to_latlon(d_metri, 0, lat_ref, lon_ref)
    p = lpp.encode_delta(lat, lon, 20.0, lat_ref, lon_ref)
    lat2, lon2, _ = lpp.decode_delta(p, lat_ref, lon_ref)
    err = lpp.distanta(lat, lon, lat2, lon2)
    print(f"{d_metri:>15} {err:>10.2f}")
