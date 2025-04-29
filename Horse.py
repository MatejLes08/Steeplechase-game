import pygame


class Horse:
    def __init__(self):
        self.DRAHA = 2000
        self.VYDRZ = 100
        self.NAROCNOST_BEH = 2000
        self.NAROCNOST_SPRINT = 3000

        self.rychlost = 0
        self.max_rychlost = 60
        self.sila = 100
        self.zataz = 0
        self.prejdene_metre = 0
        self.ostava = self.DRAHA

        #vizualiacia
        self.beh = [pygame.image.load("assets/bezi1.png"),pygame.image.load("assets/bezi2.png"),pygame.image.load("assets/bezi3.png"),pygame.image.load("assets/bezi4.png")]
        self.chodza = [pygame.image.load("assets/chodi1.png"),pygame.image.load("assets/chodi2.png"),pygame.image.load("assets/chodi3.png"),pygame.image.load("assets/chodi4.png")]
        self.statie = [pygame.image.load("assets/stoji.png")]
        
        self.player_frame_index = 0
        self.animation_speed = 0.1
        self.current_image = self.statie[0]
        self.position_x = 70
        self.position_y = 300

    def pridaj_rychlost(self):
        if self.sila > 0 and self.rychlost < self.max_rychlost:
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
            if self.sila < self.VYDRZ:
                self.zataz -= oddych_cis * 2 * bonus

        elif self.sila <= 0:
            if self.rychlost > 0:
                self.rychlost -= 4  # pomaly dobieha do zastavenia
            if self.rychlost < 0:
                self.rychlost = 0

        elif self.rychlost <= 12:
            if self.sila < self.VYDRZ:
                self.zataz -= oddych_cis

        elif self.rychlost <= 24:
            self.zataz += self.rychlost / narocnost

        elif self.rychlost < 50:
            self.zataz += self.rychlost / (narocnost - self.NAROCNOST_BEH)

        else:
            self.zataz += self.rychlost / (narocnost - self.NAROCNOST_SPRINT)

        self.sila = self.VYDRZ - self.zataz         # odoberanie energie kona
        self.prejdene_metre += self.rychlost * zrychlenie / 3.6 * 0.01 #obnovovanie prejdených metrov
    
    def update_animacia(self):
        self.player_frame_index += self.animation_speed

        if self.rychlost <= 0:
            frames = self.statie
            
        elif self.rychlost <= 12:
            frames = self.chodza
            self.animation_speed = 0.055*self.rychlost/24*len(self.chodza) #vypočitanie rýchlosti animacie podla rychlosti kona a počtu obrazkov
        elif self.rychlost > 12:
            frames = self.beh
            self.animation_speed = 0.001*self.rychlost*len(self.beh) #vypočitanie rýchlosti animacie podla rychlosti kona a počtu obrazkov
        else:
            frames = self.statie

        if self.player_frame_index >= len(frames):
            self.player_frame_index = 0

        self.current_image = frames[int(self.player_frame_index)]


    def get_rychlost(self):
        return self.rychlost

    def get_sila(self):
        return self.sila
    
    def get_ostava(self):
        return round(self.DRAHA - self.prejdene_metre)
