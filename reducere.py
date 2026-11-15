"""
Strategii de decizie: cand trimite drona o actualizare de pozitie?

Fiecare strategie primeste pozitia curenta (nord, est, in metri fata de
home) si viteza, si raspunde daca pachetul se trimite acum sau nu.
Strategiile cu prag mentin intern o copie a ceea ce "crede" receptorul,
ca sa poata estima eroarea pe care o vede el.
"""
import math

HEARTBEAT_MAX = 30.0   # secunde: nu tacem niciodata mai mult de atat


class Strategie:
    """Baza comuna: gestioneaza heartbeat-ul si primul pachet."""

    def __init__(self):
        self.t_ultim = None

    def _heartbeat_expirat(self, t):
        return self.t_ultim is not None and (t - self.t_ultim) >= HEARTBEAT_MAX

    def _primul(self):
        return self.t_ultim is None

    def _marcheaza_trimis(self, t, n, e, vn, ve):
        self.t_ultim = t


class Periodic(Strategie):
    """Trimite la intervale fixe."""

    def __init__(self, perioada):
        super().__init__()
        self.perioada = perioada

    def trimit(self, t, n, e, vn, ve):
        if self._primul():
            return True
        return (t - self.t_ultim) >= self.perioada

    def nume(self):
        return f'periodic T={self.perioada}s'


class ErrorThinning(Strategie):
    """
    Trimite cand pozitia reala s-a departat de ultima pozitie trimisa
    cu mai mult decat pragul. Receptorul presupune ca drona a ramas
    unde era ultima oara (zero-order hold).
    """

    def __init__(self, prag):
        super().__init__()
        self.prag = prag
        self.n_ultim = None
        self.e_ultim = None

    def trimit(self, t, n, e, vn, ve):
        if self._primul():
            return True
        if self._heartbeat_expirat(t):
            return True
        eroare = math.hypot(n - self.n_ultim, e - self.e_ultim)
        return eroare >= self.prag

    def _marcheaza_trimis(self, t, n, e, vn, ve):
        super()._marcheaza_trimis(t, n, e, vn, ve)
        self.n_ultim = n
        self.e_ultim = e

    def nume(self):
        return f'error-thinning d={self.prag}m'


class DeadReckoning(Strategie):
    """
    Trimite cand predictia receptorului greseste peste prag.
    Receptorul extrapoleaza liniar pe baza ultimei pozitii si viteze
    primite: pozitie_estimata = pozitie_ultima + viteza_ultima * timp_scurs.
    """

    def __init__(self, prag):
        super().__init__()
        self.prag = prag
        self.n_ultim = None
        self.e_ultim = None
        self.vn_ultim = None
        self.ve_ultim = None

    def _predictie(self, t):
        dt = t - self.t_ultim
        return (self.n_ultim + self.vn_ultim * dt,
                self.e_ultim + self.ve_ultim * dt)

    def trimit(self, t, n, e, vn, ve):
        if self._primul():
            return True
        if self._heartbeat_expirat(t):
            return True
        n_pred, e_pred = self._predictie(t)
        eroare = math.hypot(n - n_pred, e - e_pred)
        return eroare >= self.prag

    def _marcheaza_trimis(self, t, n, e, vn, ve):
        super()._marcheaza_trimis(t, n, e, vn, ve)
        self.n_ultim = n
        self.e_ultim = e
        self.vn_ultim = vn
        self.ve_ultim = ve

    def nume(self):
        return f'dead-reckoning d={self.prag}m'


def ruleaza(strategie, date):
    """
    Trece un DataFrame prin strategie si returneaza lista pachetelor
    trimise: [(t, n, e, vn, ve), ...]
    """
    pachete = []
    for _, r in date.iterrows():
        t, n, e = r['t'], r['n'], r['e']
        vn, ve = r['vx'], r['vy']
        if strategie.trimit(t, n, e, vn, ve):
            strategie._marcheaza_trimis(t, n, e, vn, ve)
            pachete.append((t, n, e, vn, ve))
    return pachete
