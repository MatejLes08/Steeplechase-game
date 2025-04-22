import json

class Terrain:
    # Konštanty
    NAROCNE_PASMO_RANGE = 300
    SPRINTERSKE_PASMO_RANGE = 400
    NAPAJADLO_RANGE = 20

    ODYCH_DEFAULT = 0.01
    ZRYCHLENIE_DEFAULT = 1
    NAROCNOST_DEFAULT = 7000
    BONUS_DEFAULT = 1

    NAROCNE_PASMO_ODYCH = 0.005
    NAROCNE_PASMO_NAROCNOST = 5000
    SPRINTERSKE_PASMO_ZRYCHLENIE = 1.25
    NAPAJADLO_BONUS = 10

    def __init__(self, mapa_path="mapa1.json"):
        print("vytvoril som sa")
        with open(mapa_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.miesto_narocneho_pasma = data["miesto_narocneho_pasma"]
        self.miesto_sprinterskeho_pasma = data["miesto_sprinterskeho_pasma"]
        self.napajadla = data["napajadla"]

    def zisti_pasmo(self, ostava):
        oddych_cis = self.ODYCH_DEFAULT
        zrychlenie = self.ZRYCHLENIE_DEFAULT
        narocnost = self.NAROCNOST_DEFAULT
        bonus = self.BONUS_DEFAULT
        terrain_type = "Cesta"

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


