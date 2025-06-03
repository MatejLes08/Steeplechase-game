import time
import terrain
from Horse import Horse
from Utils import Utils


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
        self.meno_hraca = meno_hraca

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

    def update(self, dt):
        if not self.running_game:
            return

        self.cas += dt
        if int(self.cas) >= 60:
            self.cas -= 60
            self.minuty += 1

        oddych_cis, zrychlenie, narocnost, bonus, typ_terenu = self.terrain.zisti_pasmo(self.ostava)

        if self.terrain.kontroluj_naraz(self.prejdene_metre):
            self.horse.stratena_energia()

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
            Utils.ulozit_cas(cas_str, self.meno_hraca)
            self.update_record(*self.najnizsi_cas())

        self.posun_cesty += rych * dt * 11
        self.aktualny_teren = typ_terenu

    def get_akt_draha(self):
        return self.aktualny_teren

    def najnizsi_cas(self):
        return Utils.najnizsi_cas()

    def get_akt_draha_at(self, x_position):
        """
        Vypočíta, aký typ terénu je na danom x pixeli (na obrazovke),
        prepočítané podľa posunu a šírky úseku.
        """
        # Zisti, koľko metrov od začiatku trate zodpovedá tomuto x
        meter = int(self.prejdene_metre + x_position / self.sirka_useku)
        meter = max(0, min(meter, self.DRAHA))  # clamp na rozsah trate

        _, _, _, _, pasmo = self.terrain.zisti_pasmo(self.DRAHA - meter)

        if "Náročné" in pasmo:
            return "narocne"
        elif "Šprintérske" in pasmo:
            return "sprinterske"
        elif "Napájadlo" in pasmo:
            return "napajadlo"
        else:
            return "cesta"

    def get_terrain_path(self):
        """
        Vracia zoznam typov terénu pre každý meter trate (0 až 1999).
        """
        draha = []
        for meter in range(0, self.DRAHA):  # zľava doprava (0 -> 1999)
            _, _, _, _, pasmo = self.terrain.zisti_pasmo(self.DRAHA - meter)
            if "Náročné" in pasmo:
                typ = "Náročné pásmo"
            elif "Šprintérske" in pasmo:
                typ = "Šprintérske pásmo"
            elif "Napájadlo" in pasmo:
                typ = "Napájadlo"
            else:
                typ = "Cesta"
            draha.append(typ)
        return draha

    def set_meno_hraca(self, meno):
        self.meno_hraca = meno
