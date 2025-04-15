import random

class Terrain:
    # Konštanty
    NAROCNE_PASMO_MIN = 400
    NAROCNE_PASMO_MAX = 1000
    SPRINTERSKE_PASMO_MIN = 1400
    SPRINTERSKE_PASMO_MAX = 1800

    NAPAJADLO_HORNE = 1600, 2000
    NAPAJADLO_STREDNE = 800, 1580
    NAPAJADLO_NIZKE = 20, 780

    ODYCH_DEFAULT = 0.01
    ZRYCHLENIE_DEFAULT = 1
    NAROCNOST_DEFAULT = 7000
    BONUS_DEFAULT = 1

    NAROCNE_PASMO_ODYCH = 0.005
    NAROCNE_PASMO_NAROCNOST = 5000

    NAROCNE_PASMO_RANGE = 300
    SPRINTERSKE_PASMO_RANGE = 400
    NAPAJADLO_RANGE = 20
    SPRINTERSKE_PASMO_ZRYCHLENIE = 1.25
    NAPAJADLO_BONUS = 10

    def __init__(self):
        self.miesto_narocneho_pasma = random.randint(self.NAROCNE_PASMO_MIN, self.NAROCNE_PASMO_MAX)
        self.miesto_sprinterskeho_pasma = random.randint(self.SPRINTERSKE_PASMO_MIN, self.SPRINTERSKE_PASMO_MAX)

        self.napajadla = [
            random.randint(*self.NAPAJADLO_HORNE),
            random.randint(*self.NAPAJADLO_STREDNE),
            random.randint(*self.NAPAJADLO_NIZKE),
        ]

    def zisti_pasmo(self, ostava):
        oddych_cis = self.ODYCH_DEFAULT
        zrychlenie = self.ZRYCHLENIE_DEFAULT
        narocnost = self.NAROCNOST_DEFAULT
        bonus = self.BONUS_DEFAULT
        terrain_type = "cesta"

        if self.miesto_narocneho_pasma >= ostava >= self.miesto_narocneho_pasma - self.NAROCNE_PASMO_RANGE:
            terrain_type = "Náročné pásmo"
            narocnost = self.NAROCNE_PASMO_NAROCNOST
            oddych_cis = self.NAROCNE_PASMO_ODYCH

        elif self.miesto_sprinterskeho_pasma >= ostava >= self.miesto_sprinterskeho_pasma - self.SPRINTERSKE_PASMO_RANGE:
            terrain_type = "Šprintérske pásmo"
            zrychlenie = self.SPRINTERSKE_PASMO_ZRYCHLENIE

        for napajadlo in self.napajadla:
            if napajadlo >= ostava >= napajadlo - self.NAPAJADLO_RANGE:
                terrain_type = "Napájadlo"
                bonus = self.NAPAJADLO_BONUS
                break

        return oddych_cis, zrychlenie, narocnost, bonus, terrain_type
