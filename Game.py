import time
import random
import terrain
from Horse import Horse
from Utils import Utils
from ui import Screen

class Game:
    def __init__(self, update_ui_callback, update_record_callback, horse, meno_hraca=""):
        self.DRAHA = 2000
        self.prejdene_metre = 0
        self.ostava = self.DRAHA

        self.cas = 0
        self.minuty = 0

        self.update_ui = update_ui_callback
        self.update_record = update_record_callback
        self.horse = horse
        self.meno_hraca = meno_hraca  # Nový atribút pre meno hráča

        self.terrain = terrain.Terrain()  # Inicializácia s predvolenou mapou

        self.posun_cesty = -160 # pixely posunu celej cesty
        self.sirka_useku = 66  # šírka jedného úseku v px
        self.running_game = False
        self.last_time = time.time()
        self.aktualny_teren = ""

    def set_map(self, map_json):
        # Nastaví mapu podľa zadaného JSON súboru
        self.terrain = terrain.Terrain(mapa_path=map_json)
        self.posun_cesty = -160  # Reset posunu cesty pre novú mapu
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
            Utils.ulozit_cas(cas_str, self.meno_hraca)  # Odoslanie času a mena
            self.update_record(cas_str, time.time())  # Aktualizácia rekordu s časom a časovou pečiatkou
            self.ui.current_screen = Screen.END_GAME

        self.posun_cesty = self.prejdene_metre * self.sirka_useku - 160
        self.aktualny_teren = typ_terenu

    def get_akt_draha(self):
        return self.aktualny_teren

    def najnizsi_cas(self):
        # Vráti najnižší čas a časovú pečiatku ako tuple
        return Utils.najnizsi_cas()

    def get_terrain_path(self):
        draha = []
        teren_typy = [1] * 2000

        for i in range(self.terrain.miesto_narocneho_pasma - self.terrain.NAROCNE_PASMO_RANGE,
                       self.terrain.miesto_narocneho_pasma + 1):
            if 0 <= i < len(teren_typy):
                teren_typy[i] = 2

        for i in range(self.terrain.miesto_sprinterskeho_pasma - self.terrain.SPRINTERSKE_PASMO_RANGE,
                       self.terrain.miesto_sprinterskeho_pasma + 1):
            if 0 <= i < len(teren_typy) and teren_typy[i] == 1:
                teren_typy[i] = 3

        for napajadlo in self.terrain.napajadla:
            for i in range(napajadlo - self.terrain.NAPAJADLO_RANGE, napajadlo + 1):
                if 0 <= i < len(teren_typy) and teren_typy[i] == 1:
                    teren_typy[i] = 4

        counters = {1: 0, 2: 0, 3: 0, 4: 0}

        for typ in teren_typy:
            if typ == 1:
                base = 1
            elif typ == 2:
                base = 4
            elif typ == 3:
                base = 7
            elif typ == 4:
                base = 10

            obrazok = base + counters[typ]
            draha.append(obrazok)
            counters[typ] = (counters[typ] + 1) % 3
        draha.reverse()
        # Pridaj start a ciel bez reverse
        draha[0] = 0         # start.png
        draha[-1] = 13       # ciel.png

        print("410:", draha[410])
        print("dlzka: ", len(draha))
        
        return draha

    def set_meno_hraca(self, meno):
        self.meno_hraca = meno  # Metóda na aktualizáciu mena

    def set_ui(self, ui):
        self.ui = ui