"""
Reconstruieste traiectoria la receptor, din pachetele primite.
Doua moduri:
  - 'hold': pozitia ramane la ultima valoare primita
  - 'extrapolare': pozitia avanseaza cu ultima viteza primita
"""
import bisect


class Receptor:
    def __init__(self, pachete, mod='hold'):
        """pachete: lista de (t, n, e, vn, ve), ordonata dupa t"""
        self.pachete = pachete
        self.mod = mod
        self.timpi = [p[0] for p in pachete]

    def pozitie_la(self, t):
        """Ce crede receptorul despre pozitia dronei la momentul t."""
        i = bisect.bisect_right(self.timpi, t) - 1
        if i < 0:
            return None          # inca nu a primit niciun pachet
        t_p, n, e, vn, ve = self.pachete[i]
        if self.mod == 'hold':
            return n, e
        dt = t - t_p
        return n + vn * dt, e + ve * dt

    def varsta_la(self, t):
        """Age of Information: cat de veche e informatia la momentul t."""
        i = bisect.bisect_right(self.timpi, t) - 1
        if i < 0:
            return None
        return t - self.pachete[i][0]
