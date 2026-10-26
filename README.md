# MAVLite — telemetrie MAVLink comprimată pe canale LoRa

Pipeline și studiu experimental pentru transmiterea telemetriei UAV
(MAVLink) printr-un canal LoRa point-to-multipoint, folosind codare
Cayenne LPP.

Proiect realizat în cadrul cursului *Research Industry Projects*
(master Tehnologii Internet), pe o temă propusă de un partener industrial
din Brașov.

---

## Problema

O dronă produce telemetrie MAVLink cu zeci de mesaje pe secundă. Un canal
LoRa permite zeci de octeți la câteva secunde, sub restricția de duty cycle
de 1% (EU868). Întrebarea este ce se pierde când reduci fluxul și cât costă
fiecare compromis.

Întrebarea de cercetare:

> Pentru telemetria MAVLink transportată prin Cayenne LPP pe un canal LoRa
> P2MP cu duty cycle, care combinație de codare, strategie de reducere și
> nivel de autentificare menține eroarea de poziție sub un prag dat pentru
> cât mai multe drone?

## Contribuții

1. Cuantificarea costului de reprezentare: MAVLink vs. Cayenne LPP
   (standard, custom, delta), în octeți și eroare de cuantizare.
2. Evaluarea strategiilor de reducere pe traiectorii reale de UAV,
   cu eroare de poziție și Age of Information ca metrici. *(în lucru)*
3. Costul securității în bugetul de transmisie: octeți, airtime,
   număr de drone servite. *(planificat)*
4. Pipeline reproductibil, cu date și cod.

---

## Instalare

Mediul de dezvoltare presupune Linux (testat pe Ubuntu 24.04 prin WSL2).

```bash
# dependențe de sistem
sudo apt install -y git python3 python3-pip python3-venv build-essential

# mediul Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Pentru generarea datelor e nevoie de ArduPilot SITL:

```bash
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
```

## Utilizare

### Generarea datelor

Pornește simulatorul:

```bash
cd ~/ardupilot/ArduCopter
sim_vehicle.py --console --out=127.0.0.1:14551
```

Așteaptă `pre-arm good`, apoi în consola MAVProxy:
