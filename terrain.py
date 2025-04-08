import random

class Terrain:
    def __init__(self):
        self.miesto_narocneho_pasma = random.randint(400, 1000)
        self.miesto_sprinterskeho_pasma = random.randint(1400, 1800)

        napajadla = [
            random.randint(1600, 2000),
            random.randint(800, 1580),
            random.randint(20, 780),
        ]
        self.napajadla = napajadla

    def zisti_pasmo(self, ostava):
        oddych_cis = 0.01
        zrychlenie = 1
        narocnost = 7000
        bonus = 1
        terrain_type = "cesta"

        if self.miesto_narocneho_pasma >= ostava >= self.miesto_narocneho_pasma - 300:
            terrain_type = "Náročné pásmo"
            narocnost = 5000
            oddych_cis = 0.005

        elif self.miesto_sprinterskeho_pasma >= ostava >= self.miesto_sprinterskeho_pasma - 400:
            terrain_type = "Šprintérske pásmo"
            zrychlenie = 1.25

        for napajadlo in self.napajadla:
            if napajadlo >= ostava >= napajadlo - 20:
                terrain_type = "Napájadlo"
                bonus = 10
                break

        return oddych_cis, zrychlenie, narocnost, bonus, terrain_type
