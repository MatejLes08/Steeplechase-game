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
        self.pretazenie = 0
        self.prejdene_metre = 0
        self.ostava = self.DRAHA

        # načítanie sprite sheetov s animáciami
        self.beh = self.nacitaj_sprite_sheet("assets/Horse_Run.png", 60)
        self.chodza = self.nacitaj_sprite_sheet("assets/Horse_Walk.png", 60)
        self.statie = self.nacitaj_sprite_sheet("assets/Horse_Idle.png", 60)

        self.player_frame_index = 0
        self.animation_speed = 0.1
        self.current_image = self.statie[0]
        self.position_x = 70
        self.position_y = 300

    def nacitaj_sprite_sheet(self, path, frame_width):
        sheet = pygame.image.load(path)
        sheet.set_colorkey((255, 255, 255))  # odstránenie bieleho pozadia

        width, height = sheet.get_size()
        frames = []

        for i in range(width // frame_width):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, height)).copy()
            frame = pygame.transform.flip(frame, True, False)
            frame = pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2))
            frames.append(frame)

        return frames

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
                self.pretazenie = -oddych_cis * 2 * bonus  # oddych
            else:
                self.pretazenie = 0

        elif self.sila <= 0:
            if self.rychlost > 0:
                self.rychlost -= 4  # pomaly dobieha do zastavenia
            if self.rychlost < 0:
                self.rychlost = 0
            self.pretazenie = 0  # žiadne ďalšie zvyšovanie únavy

        elif self.rychlost <= 12:
            if self.sila < self.VYDRZ:
                self.pretazenie = -oddych_cis  # mierny oddych

        elif self.rychlost <= 24:
            self.pretazenie = self.rychlost / narocnost

        elif self.rychlost < 50:
            self.pretazenie = self.rychlost / (narocnost - self.NAROCNOST_BEH)

        else:
            self.pretazenie = self.rychlost / (narocnost - self.NAROCNOST_SPRINT)

        self.sila -= self.pretazenie         # odoberanie energie kona
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

    def detekuj_koliziu_s_prekazkami(self, prekazky):
        kon_rect = pygame.Rect(self.position_x, self.position_y, self.current_image.get_width(), self.current_image.get_height())
        for prekazka in prekazky:
            if kon_rect.colliderect(prekazka):
                self.sila -= 10
                if self.sila < 0:
                    self.sila = 0
                break

    def get_rychlost(self):
        return self.rychlost

    def get_sila(self):
        return self.sila

    def get_ostava(self):
        return round(self.DRAHA - self.prejdene_metre)