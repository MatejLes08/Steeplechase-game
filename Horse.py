class Horse:
    def __init__(self):
        self.rychlost = 0
        self.max_rychlost = 60
        self.vydrz = 100
        self.sila = 100
        self.zataz = 0

    def pridaj_rychlost(self):
        if self.sila != 0 and self.rychlost < self.max_rychlost:
            self.rychlost += 4
            if self.rychlost > self.max_rychlost:
                self.rychlost = self.max_rychlost

    def spomal_rychlost(self):
        if self.rychlost > 0:
            self.rychlost -= 4
            if self.rychlost < 0:
                self.rychlost = 0

    def aktualizuj_silu(self, oddych_cis, zrychlenie, narocnost, bonus):
        if self.rychlost == 0:
            if self.sila < 100:
                self.zataz -= oddych_cis * 2 * bonus

        elif self.sila <= 0:
            self.rychlost = 4

        elif self.rychlost <= 12:
            if self.sila < 100:
                self.zataz -= oddych_cis

        elif self.rychlost <= 24:
            self.zataz += self.rychlost / narocnost

        elif self.rychlost < 50:
            self.zataz += self.rychlost / (narocnost - 2000)

        else:
            self.zataz += self.rychlost / (narocnost - 3000)

        # Zabezpečiť, že sila sa nezvýši nad maximum alebo nezníži pod 0
        self.sila = max(0, min(self.vydrz - self.zataz, 100))

    def get_rychlost(self):
        return self.rychlost

    def get_sila(self):
        return self.sila
