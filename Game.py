import time
import random
import terrain
from Horse import Horse
from Utils import Utils  

class Game:
    def __init__(self, update_ui_callback, update_record_callback, horse):
        self.DRAHA = 2000
        self.prejdene_metre = 0
        self.ostava = self.DRAHA

        self.cas = 0
        self.minuty = 0

        self.update_ui = update_ui_callback
        self.update_record = update_record_callback
        self.horse = horse

        self.terrain = terrain.Terrain()

        self.posun_cesty = 0  # pixely posunu celej cesty
        self.sirka_useku = 62  # šírka jedného úseku v px
        self.running_game = False
        self.last_time = time.time()
        self.aktualny_teren = ""

    def start_race(self):
        self.prejdene_metre = 0
        self.cas = 0
        self.minuty = 0
        self.running_game = True 
        self.ostava = self.DRAHA
        
    def update(self, dt):  # dt = čas od poslednej aktualizácie
        if not self.running_game:
            return

        self.cas += dt
        if int(self.cas) >= 60:
            self.cas -= 60
            self.minuty += 1

        oddych_cis, zrychlenie, narocnost, bonus, typ_terenu = self.terrain.zisti_pasmo(self.ostava)

        # Kontrola nárazu do prekážky na preddefinovaných metroch
        if self.terrain.kontroluj_naraz(self.prejdene_metre):
            self.horse.stratena_energia()  # Zníženie energie koňa po náraze do prekážky

        self.horse.aktualizuj_silu(oddych_cis, zrychlenie, narocnost, bonus)
        rych = self.horse.get_rychlost()
        sila = self.horse.get_sila()
        self.ostava = self.horse.get_ostava()
        self.prejdene_metre = self.horse.prejdene_metre
        self.pretazenie = self.horse.pretazenie

        cas_str = f"{self.minuty}:{int(self.cas):02d}:{int((self.cas - int(self.cas)) * 100):02d}"
        self.update_ui(int(rych * zrychlenie), self.ostava, int(sila), cas_str, self.pretazenie * 100)

        if self.prejdene_metre >= self.DRAHA:
            self.running_game = False
            Utils.ulozit_cas(cas_str)
            self.update_record(self.najnizsi_cas())

        self.posun_cesty += rych * dt * 11
        self.aktualny_teren = typ_terenu

    def get_akt_draha(self):
        return self.aktualny_teren

    def najnizsi_cas(self):
        return Utils.najnizsi_cas()

    def get_terrain_path(self):
        draha = []
        for meter in range(2000, 0, -1):
            typ = "Cesta"
            if self.terrain.miesto_narocneho_pasma >= meter >= self.terrain.miesto_narocneho_pasma - self.terrain.NAROCNE_PASMO_RANGE:
                typ = "Náročné pásmo"
            elif self.terrain.miesto_sprinterskeho_pasma >= meter >= self.terrain.miesto_sprinterskeho_pasma - self.terrain.SPRINTERSKE_PASMO_RANGE:
                typ = "Šprintérske pásmo"
            for napajadlo in self.terrain.napajadla:
                if napajadlo >= meter >= napajadlo - self.terrain.NAPAJADLO_RANGE:
                    typ = "Napájadlo"
                    break
            draha.append(typ)
        return draha
