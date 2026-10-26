"""
Encodere pentru pozitia unui UAV, in trei variante:
  - lpp_standard: tipul GPS Location din Cayenne LPP (rezolutie 0.0001 grade)
  - lpp_custom:   acelasi format, dar cu rezolutie mai fina (0.000001 grade)
  - delta:        offset in metri fata de o pozitie de referinta
"""
import struct
import math

# ---- utilitare -----------------------------------------------------------

def int_to_bytes_signed(value, n):
    """Scrie un intreg cu semn pe n octeti, big-endian."""
    return value.to_bytes(n, byteorder='big', signed=True)

def bytes_to_int_signed(b):
    return int.from_bytes(b, byteorder='big', signed=True)


# ---- varianta 1: Cayenne LPP standard ------------------------------------
# GPS Location: lat si lon pe 3 octeti fiecare (unitate 0.0001 grade),
# altitudine pe 3 octeti (unitate 0.01 m). Plus 2 octeti de header.

LPP_HEADER = 2          # canal + tip
GPS_TYPE = 0x88

def encode_lpp_standard(lat, lon, alt, canal=1):
    lat_i = round(lat * 1e4)
    lon_i = round(lon * 1e4)
    alt_i = round(alt * 1e2)
    return (bytes([canal, GPS_TYPE])
            + int_to_bytes_signed(lat_i, 3)
            + int_to_bytes_signed(lon_i, 3)
            + int_to_bytes_signed(alt_i, 3))

def decode_lpp_standard(payload):
    lat = bytes_to_int_signed(payload[2:5]) / 1e4
    lon = bytes_to_int_signed(payload[5:8]) / 1e4
    alt = bytes_to_int_signed(payload[8:11]) / 1e2
    return lat, lon, alt


# ---- varianta 2: LPP cu rezolutie fina -----------------------------------
# lat si lon pe 4 octeti (unitate 0.000001 grade), altitudine pe 3 octeti.

def encode_lpp_custom(lat, lon, alt, canal=1):
    lat_i = round(lat * 1e6)
    lon_i = round(lon * 1e6)
    alt_i = round(alt * 1e2)
    return (bytes([canal, GPS_TYPE])
            + int_to_bytes_signed(lat_i, 4)
            + int_to_bytes_signed(lon_i, 4)
            + int_to_bytes_signed(alt_i, 3))

def decode_lpp_custom(payload):
    lat = bytes_to_int_signed(payload[2:6]) / 1e6
    lon = bytes_to_int_signed(payload[6:10]) / 1e6
    alt = bytes_to_int_signed(payload[10:13]) / 1e2
    return lat, lon, alt


# ---- varianta 3: delta fata de o referinta -------------------------------
# offset nord/est in metri, pe 2 octeti fiecare (unitate 0.1 m,
# deci +/- 3276.7 m fata de referinta). Altitudine pe 2 octeti (0.1 m).

def encode_delta(lat, lon, alt, lat_ref, lon_ref, canal=1):
    dn, de = latlon_to_ne(lat, lon, lat_ref, lon_ref)
    dn_i = max(-32768, min(32767, round(dn * 10)))
    de_i = max(-32768, min(32767, round(de * 10)))
    alt_i = max(-32768, min(32767, round(alt * 10)))
    return (bytes([canal, GPS_TYPE])
            + int_to_bytes_signed(dn_i, 2)
            + int_to_bytes_signed(de_i, 2)
            + int_to_bytes_signed(alt_i, 2))

def decode_delta(payload, lat_ref, lon_ref):
    dn = bytes_to_int_signed(payload[2:4]) / 10.0
    de = bytes_to_int_signed(payload[4:6]) / 10.0
    alt = bytes_to_int_signed(payload[6:8]) / 10.0
    lat, lon = ne_to_latlon(dn, de, lat_ref, lon_ref)
    return lat, lon, alt


# ---- conversii geografice ------------------------------------------------

R_PAMANT = 6378137.0    # raza ecuatoriala, metri

def latlon_to_ne(lat, lon, lat_ref, lon_ref):
    """Offset aproximativ in metri (nord, est) fata de referinta."""
    dn = math.radians(lat - lat_ref) * R_PAMANT
    de = math.radians(lon - lon_ref) * R_PAMANT * math.cos(math.radians(lat_ref))
    return dn, de

def ne_to_latlon(dn, de, lat_ref, lon_ref):
    lat = lat_ref + math.degrees(dn / R_PAMANT)
    lon = lon_ref + math.degrees(de / (R_PAMANT * math.cos(math.radians(lat_ref))))
    return lat, lon

def distanta(lat1, lon1, lat2, lon2):
    """Distanta aproximativa in metri intre doua puncte apropiate."""
    dn, de = latlon_to_ne(lat2, lon2, lat1, lon1)
    return math.hypot(dn, de)
