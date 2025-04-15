import time
import random
import terrain
from Utils import Utils  

class Game:
    def __init__(self, update_ui_callback, update_record_callback):
        self.DRAHA = 2000
        self.KON_VYDRZ = 100
        self.NAROCNOST_BEH = 2000
        self.NAROCNOST_SPRINT = 3000
        self.prejdene_metre = 0
        self.kon_rychlost = 0
        self.zataz = 0
        self.sila = 100

        self.cas = 0
        self.minuty = 0

        self.update_ui = update_ui_callback
        self.update_record = update_record_callback

        self.terrain = terrain.Terrain()

        self.running = False
        self.last_time = time.time()

    def start_race(self):
        self.prejdene_metre = 0
        self.cas = 0
        self.minuty = 0
        self.zataz = 0
        self.sila = 100
        self.kon_rychlost = 0
        self.running = True 

        self.ostava = self.DRAHA

    def update(self, dt):  # dt = čas od poslednej aktualizácie
        if not self.running:
            return

        self.cas += dt
        # rovnaký výpočet logiky ako doteraz, ale bez time.sleep()

        if int(self.cas) >= 60:
            self.cas -= 60
            self.minuty += 1

        oddych_cis, zrychlenie, narocnost, bonus, typ_terenu = self.terrain.zisti_pasmo(self.ostava)

        if self.kon_rychlost == 0:
            if self.sila < self.KON_VYDRZ:
                self.zataz -= oddych_cis * 2 * bonus

        elif self.sila <= 0:
            self.kon_rychlost = 4

        elif self.kon_rychlost <= 12:
            if self.sila < self.KON_VYDRZ:
                self.zataz -= oddych_cis

        elif self.kon_rychlost <= 24:
            self.zataz += self.kon_rychlost / narocnost

        elif self.kon_rychlost < 50:
            self.zataz += self.kon_rychlost / (narocnost - self.NAROCNOST_BEH)

        else:
            self.zataz += self.kon_rychlost / (narocnost - self.NAROCNOST_SPRINT)

        self.sila = self.KON_VYDRZ - self.zataz         # odoberanie energie kona
        self.prejdene_metre += self.kon_rychlost * zrychlenie / 3.6 * 0.01 #obnovovanie prejdených metrov
        self.ostava = round(self.DRAHA - self.prejdene_metre)
        
        cas_str = f"{self.minuty}:{int(self.cas):02d}:{int((self.cas - int(self.cas)) * 100):02d}"

        self.update_ui(int(self.kon_rychlost * zrychlenie), self.ostava, int(self.sila), cas_str)


        if self.prejdene_metre >= self.DRAHA:
            self.running = False
            Utils.ulozit_cas(cas_str)
            self.update_record(self.najnizsi_cas())

    def stop(self):
        self.bezi = False 

    def najnizsi_cas(self):
        return Utils.najnizsi_cas()
