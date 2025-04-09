import time
import random
import terrain
from Utils import Utils  

class Game:
    def __init__(self, update_ui_callback, update_record_callback):
        self.prejdene_metre = 0
        self.draha = 2000
        self.kon_rychlost = 0
        self.kon_max_rychlost = 60
        self.kon_vydrz = 100
        self.zataz = 0
        self.sila = 100

        self.cas = 0
        self.minuty = 0

        self.update_ui = update_ui_callback
        self.update_record = update_record_callback

        self.terrain = terrain.Terrain()


    def start_race(self):
        self.prejdene_metre = 0
        self.cas = 0
        self.minuty = 0
        self.zataz = 0
        self.sila = 100
        self.kon_rychlost = 0

        ostava = self.draha

        while self.prejdene_metre < self.draha:
            time.sleep(0.01)

            self.cas += 0.01
            if int(self.cas) >= 60:
                self.cas -= 60
                self.minuty += 1

            oddych_cis, zrychlenie, narocnost, bonus, typ_terenu = self.terrain.zisti_pasmo(ostava)

            if self.kon_rychlost == 0:
                if self.sila < 100:
                    self.zataz -= oddych_cis * 2 * bonus

            elif self.sila <= 0:
                self.kon_rychlost = 4

            elif self.kon_rychlost <= 12:
                if self.sila < 100:
                    self.zataz -= oddych_cis

            elif self.kon_rychlost <= 24:
                self.zataz += self.kon_rychlost / narocnost

            elif self.kon_rychlost < 50:
                self.zataz += self.kon_rychlost / (narocnost - 2000)

            else:
                self.zataz += self.kon_rychlost / (narocnost - 3000)

            self.sila = self.kon_vydrz - self.zataz         # odoberanie energie kona
            self.prejdene_metre += self.kon_rychlost * zrychlenie / 3.6 * 0.01 #obnovovanie prejdených metrov
            ostava = round(self.draha - self.prejdene_metre)
            
            cas_str = f"{self.minuty}:{int(self.cas):02d}"
            self.update_ui(int(self.kon_rychlost * zrychlenie), ostava, int(self.sila), cas_str)

        Utils.ulozit_cas(cas_str)
        self.update_record(self.najnizsi_cas())

