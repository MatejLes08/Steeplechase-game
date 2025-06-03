# =====================================
# 🔧 1. IMPORTY A ENUMY
# =====================================
import pygame
from enum import Enum
from Utils import Utils
from Horse import Horse

class Screen(Enum):
    MENU = 1
    MAP_VIEW = 2
    GAME = 3


# =====================================
# 🎮 2. HLAVNÁ TRIEDA UI
# =====================================
class UI:
    def __init__(self, pridaj_callback, spomal_callback, koniec_callback, gamec):
        pygame.init()
        self.game = gamec

        # --- Rozmery okna ---
        self.width = 820
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Steeplchase preteky")

        # --- Fonty ---
        self.title_font = pygame.font.SysFont(None, 60)
        self.font = pygame.font.SysFont(None, 40)
        self.fontMetre = pygame.font.SysFont(None, 110)
        self.fontCas = pygame.font.SysFont("Arial", 70)

        # --- Farby ---
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.DARKGRAY = (100, 100, 100)
        self.BLACK = (0, 0, 0)
        self.ORANGE = (57, 183, 177)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.LIGHT_BLUE = (173, 216, 230)

        # --- Herné premenné ---
        self.rychlost = 0
        self.energia = 100
        self.neprejdenych = 0
        self.aktualna_draha = ""
        self.stopky = "0:00:00"
        self.rekord = Utils.najnizsi_cas()
        self.pretazenie = 0

        # --- Meno hráča ---
        self.meno_hraca = ""
        self.meno_input = ""
        self.input_rect = pygame.Rect(self.width // 2 - 150, 180, 300, 40)
        self.active_input = False

        # --- Tlačidlá v hre ---
        self.button_cancel = pygame.Rect(32, 433, 150, 50)
        self.button_decrease = pygame.Rect(216, 433, 150, 50)
        self.button_increase = pygame.Rect(416, 433, 150, 50)

        # --- Tlačidlá MENU ---
        self.button_start_menu = pygame.Rect(300, 250, 200, 50)
        self.button_exit_menu = pygame.Rect(300, 350, 200, 50)

        # --- Tlačidlá MAP_VIEW ---
        mid_x = self.width // 2
        self.button_play_map = pygame.Rect(mid_x + 70, 380, 120, 40)
        self.button_back_map = pygame.Rect(mid_x + 220, 380, 120, 40)

        # --- Callbacks ---
        self.pridaj_callback = pridaj_callback
        self.spomal_callback = spomal_callback
        self.koniec_callback = koniec_callback

        # --- Terén a biomy ---
        self.draha = self.game.get_terrain_path()
        self.biome_images = self.load_biome_images()

        # --- Skóre ---
        self.scores = []
        self.my_score = None

        # --- Počiatočná obrazovka ---
        self.current_screen = Screen.MENU


# =====================================
# 🌍 3. TERÉN A BIOMY
# =====================================
    def load_biome_images(self):
        biomes = ["narocne", "cesta", "sprinterske", "napajadlo"]
        biome_images = {}
        for biome in biomes:
            biome_images[biome] = [
                pygame.image.load(f"assets/{biome}{i}.png").convert_alpha()
                for i in range(3)
            ]
        return biome_images

    def get_biome_at_meter(self, meter):
        # meter je vzdialenosť od cieľa (napr. od 0 do 2000)

        if self.game.terrain.miesto_narocneho_pasma - self.game.terrain.NAROCNE_PASMO_RANGE <= meter <= self.game.terrain.miesto_narocneho_pasma:
            return "narocne"
        elif self.game.terrain.miesto_sprinterskeho_pasma - self.game.terrain.SPRINTERSKE_PASMO_RANGE <= meter <= self.game.terrain.miesto_sprinterskeho_pasma:
            return "sprinterske"
        elif any(napajadlo - self.game.terrain.NAPAJADLO_RANGE <= meter <= napajadlo for napajadlo in self.game.terrain.napajadla):
            return "napajadlo"
        else:
            return "cesta"


    def get_biome_images(self, world_x):
        for i in range(len(self.biomes) - 1):
            b1 = self.biomes[i]
            b2 = self.biomes[i + 1]
            if b1["x_start"] <= world_x < b2["x_start"]:
                t = (world_x - b1["x_start"]) / (b2["x_start"] - b1["x_start"])
                return b1["image"], b2["image"], b1["decoration"], b2["decoration"], t
        b = self.biomes[-1]
        return b["image"], b["image"], b["decoration"], b["decoration"], 0.0

    def get_current_biome_name(self, world_x):
        for i in range(len(self.biomes) - 1):
            if self.biomes[i]["x_start"] <= world_x < self.biomes[i + 1]["x_start"]:
                return self.biomes[i]["name"]
        return self.biomes[-1]["name"]


# =====================================
# 🧱 4. UI POMOCNÉ FUNKCIE
# =====================================
    def draw_energy(self, screen, font, value, x, y, width=150, height=30, green=(0,255,0), yellow=(255,255,0), red=(255,0,0), black=(0,0,0)):
        value = max(0, min(100, value))
        bar_width = int((value / 100) * width)
        if value > 66:
            bar_color = green
        elif value > 33:
            bar_color = yellow
        else:
            bar_color = red
        rect_bg = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (150, 150, 150), rect_bg)
        pygame.draw.rect(screen, black, rect_bg, 2)
        rect_fill = pygame.Rect(x, y, bar_width, height)
        pygame.draw.rect(screen, bar_color, rect_fill)
        text = font.render(f"{value}%", True, black)
        text_rect = text.get_rect(center=rect_bg.center)
        screen.blit(text, text_rect)

    def draw_text(self, screen, font_obj, label, value, x, y, color=(0, 0, 0)):
        text = font_obj.render(f"{label}: {value}", True, color)
        screen.blit(text, (x, y))

    def render_button_text(self, screen, font_obj, text, rect, color=(0, 0, 0)):
        label = font_obj.render(text, True, color)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)


# =====================================
# 🏁 5. VYKRESLENIE MENU A MAP VIEW
# =====================================
    def draw_menu(self):
        """
        Vykreslí hlavné MENU obsluhujúce zadanie mena hráča
        """
        self.screen.fill(self.ORANGE)  # pozadie
        title = self.title_font.render("Steeplechase preteky", True, self.BLACK)
        # vycentrovanie titulku na šírku okna
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Label a input pole pre meno hráča
        meno_label = self.font.render("Meno hráča:", True, self.BLACK)
        label_rect = meno_label.get_rect(center=(self.width // 2, 150))
        self.screen.blit(meno_label, label_rect)

        pygame.draw.rect(self.screen, self.WHITE, self.input_rect)
        border_color = self.BLACK if self.active_input else self.DARKGRAY
        pygame.draw.rect(self.screen, border_color, self.input_rect, 2)
        meno_text = self.font.render(self.meno_input, True, self.BLACK)
        self.screen.blit(meno_text, (self.input_rect.x + 10, self.input_rect.y + 5))

        # Tlačidlá MENU (Hrať, Ukončiť)
        pygame.draw.rect(self.screen, self.GRAY, self.button_start_menu)
        pygame.draw.rect(self.screen, self.GRAY, self.button_exit_menu)
        def render_button_text(text, rect):
            lbl = self.font.render(text, True, self.BLACK)
            lbl_rect = lbl.get_rect(center=rect.center)
            self.screen.blit(lbl, lbl_rect)
        render_button_text("Hrať", self.button_start_menu)
        render_button_text("Ukončiť", self.button_exit_menu)

        pygame.display.flip()  # zobraziť všetko na obrazovke

    def draw_map_view(self):
        """
        Vykreslí výber mapy rozdelený na dve časti:
          - ľavá: rebríček
          - pravá: podrobnosti mapy (názov, obrázok, tlačidlá)
        """
        self.screen.fill(self.ORANGE)
        half = self.width // 2

        # ### Farby pre pozadie blokov ###
        pygame.draw.rect(self.screen, self.ORANGE,  (0, 0, half, self.height))
        pygame.draw.rect(self.screen, self.ORANGE, (half, 0, half, self.height))

        # --- ľavá strana: rebríček ---
        # Vykreslenie názvu "Rebríček" vycentrovaného v ľavom bloku
        title_surf = self.title_font.render("Rebríček", True, self.BLACK)
        # x-ová pozícia = stred bloku minus polovica šírky textu
        x_center = (half // 2) - (title_surf.get_width() // 2)
        self.screen.blit(title_surf, (x_center, 10))

        # Ak zatiaľ nemáme žiadne skóre, zobrazím placeholder text
        y0 = 60
        if not self.scores:
            placeholder = self.font.render("Žiadne údaje", True, self.DARKGRAY)
            self.screen.blit(placeholder, (20, y0))
        else:
            # Inak vypíšem prvých 5
            for i, (rank, name, time_str) in enumerate(self.scores[:5]):
                txt = f"{rank}. {name}  {time_str}"
                self.screen.blit(self.font.render(txt, True, self.BLACK), (20, y0 + i*40))
            # Kreslím oddelovaciu čiaru pod piatym miestom
            pygame.draw.line(self.screen, self.DARKGRAY,
                             (20, y0 + 5*40 + 10),
                             (half - 20, y0 + 5*40 + 10), 2)
            # vypíšem aj tvoje miesto červeným textom (ak existuje)
            if self.my_score:
                r, n, t = self.my_score
                txt = f"{r}. {n}  {t}"
                self.screen.blit(self.font.render(txt, True, self.RED), (20, y0 + 5*40 + 30))

        # --- pravá strana: podrobnosti mapy ---
        # Získanie názvu mapy cez volanie metódy (fallback na "MAPA")
        map_name = getattr(self.game, 'get_map_name', lambda: "MAPA")()
        lbl_map = self.font.render(map_name, True, self.BLACK)
        mx = half + (half - lbl_map.get_width()) // 2
        self.screen.blit(lbl_map, (mx, 20))

        # Obrázok mapy (pokúsim sa načítať, inak rámček)
        try:
            raw_img = pygame.image.load(self.draha).convert()
            map_img = pygame.transform.scale(raw_img, (half-40, 250))
            self.screen.blit(map_img, (half+20, 60))
        except Exception:
            pygame.draw.rect(self.screen, self.DARKGRAY,
                             (half+20, 60, half-40, 250), 2)

        # Tlačidlá Hrať a Späť v pravom bloku
        pygame.draw.rect(self.screen, self.GRAY, self.button_play_map)
        pygame.draw.rect(self.screen, self.GRAY, self.button_back_map)
        def btn_text(text, rect):
            lbl = self.font.render(text, True, self.BLACK)
            lbl_rect = lbl.get_rect(center=rect.center)
            self.screen.blit(lbl, lbl_rect)
        btn_text("Hrať", self.button_play_map)
        btn_text("Späť", self.button_back_map)

        pygame.display.flip()


# =====================================
# 🏇 6. VYKRESLENIE GAME UI + CESTA
# =====================================
    def draw_ui(self, horse):
        print("draw_ui() sa volá!")
        # zvyšok tvojej funkcie...

        self.screen.fill(self.ORANGE)

        self.draw_text(self.screen, self.font, "Rýchlosť", self.rychlost, 20, 60)
        self.draw_energy(self.screen, self.font, self.energia, 91, 20, green=self.GREEN, yellow=self.YELLOW, red=self.RED, black=self.BLACK)

        self.metre = self.fontMetre.render(str(self.neprejdenych) + "m", True, self.BLACK)
        self.metre_rect = self.metre.get_rect(center=(self.screen.get_width() // 2, 40))
        self.screen.blit(self.metre, self.metre_rect)

        self.draw_text(self.screen, self.font, "Terén", self.aktualna_draha, 20, 100)
        if self.game:
            self.aktualna_draha = self.game.get_akt_draha()
        self.draw_text(self.screen, self.font, "Terén", self.aktualna_draha, 20, 100)

        self.cas = self.fontCas.render(self.stopky, True, self.BLACK)
        self.cas_rect = self.cas.get_rect(center=(700, 40))
        self.screen.blit(self.cas, self.cas_rect)

        self.draw_text(self.screen, self.font, "Rekord", self.rekord, 580, 70)
        self.draw_text(self.screen, self.font, "Preťaženie", self.pretazenie, 580, 110)

        # Posúvajúce sa pásy (cesta)
        if self.game:
            posun = self.game.posun_cesty
            sirka = self.game.sirka_useku
            self.offset = -int(posun % sirka)
            start_index = int(posun // sirka) - 1
            world_x = posun

            for i in range(15):
                sirka = self.game.sirka_useku
                posun = self.game.posun_cesty
                self.offset = -int(posun % sirka)
                start_meter = int(posun // sirka) - 1  # meter offset

                frame_index = (int(posun // 10)) % 3  # rýchlosť animácie (napr. každých 10 pixelov posunu zmena frame)

                for i in range(15):
                    x_pos = i * sirka + self.offset
                    meter = start_meter + i * sirka

                    biome1_name = self.get_biome_at_meter(meter)
                    biome2_name = self.get_biome_at_meter(meter + sirka)

                    t = ((meter % sirka) / sirka)  # interpolácia medzi biome1 a biome2

                    img1 = self.biome_images[biome1_name][frame_index]
                    img2 = self.biome_images[biome2_name][frame_index]

                    img1_scaled = pygame.transform.scale(img1, (sirka, 200))
                    img2_scaled = pygame.transform.scale(img2, (sirka, 200))

                    blended_surface = pygame.Surface((sirka, 200), pygame.SRCALPHA)

                    img1_scaled.set_alpha(int(255 * (1 - t)))
                    img2_scaled.set_alpha(int(255 * t))

                    blended_surface.blit(img1_scaled, (0, 0))
                    blended_surface.blit(img2_scaled, (0, 0))

                    self.screen.blit(blended_surface, (x_pos, 220))
        pygame.display.flip()



# =====================================
# 🖱️ 7. OVLÁDANIE A UDALOSTI
# =====================================
    def handle_events(self):
        # Spracovanie udalostí (klávesy, myš)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("Klik na pozícii:", event.pos)
                print("Aktuálna obrazovka:", self.current_screen)

                if self.current_screen == Screen.MAP_VIEW:
                    print("Sme v MAP_VIEW...")
                    if self.button_play_map.collidepoint(event.pos):
                        print("Klik na tlačidlo HRAŤ!")
                        self.current_screen = Screen.GAME

            if event.type == pygame.MOUSEBUTTONDOWN:
                # MENU obrazovka: ovládanie inputu + tlačidiel
                if self.current_screen == Screen.MENU:
                    self.active_input = self.input_rect.collidepoint(event.pos)
                    if self.button_start_menu.collidepoint(event.pos) and self.meno_input.strip():
                        self.meno_hraca = self.meno_input.strip()
                        # ... načítanie leaderboardu ...
                        self.current_screen = Screen.MAP_VIEW
                    elif self.button_exit_menu.collidepoint(event.pos):
                        return False

                # MAP_VIEW obrazovka: prehľad mapy
                elif self.current_screen == Screen.MAP_VIEW:
                    if self.button_play_map.collidepoint(event.pos):
                        # Prepne len obrazovku, hra sa spustí v draw_ui/Game logike
                        self.current_screen = Screen.GAME
                    elif self.button_back_map.collidepoint(event.pos):
                        self.current_screen = Screen.MENU

                # GAME obrazovka: pôvodné tlačidlá v hre
                elif self.current_screen == Screen.GAME:
                    if self.button_cancel.collidepoint(event.pos):
                        return False
                    elif self.button_decrease.collidepoint(event.pos):
                        self.spomal_callback()
                    elif self.button_increase.collidepoint(event.pos):
                        self.pridaj_callback()

            # Spracovanie písania mena v MENU
            if event.type == pygame.KEYDOWN and self.current_screen == Screen.MENU and self.active_input:
                if event.key == pygame.K_RETURN:
                    self.active_input = False
                elif event.key == pygame.K_BACKSPACE:
                    self.meno_input = self.meno_input[:-1]
                elif len(self.meno_input) < 20:
                    self.meno_input += event.unicode

        return True


# =====================================
# 🔁 8. OSTATNÉ FUNKCIE
# =====================================
    def set_game(self, game):
        self.game = game

    def run(self, horse):
        # Hlavná slučka aplikácie
        clock = pygame.time.Clock()
        dt = 0.0
        self.game.running = True

        while self.game.running:
            self.game.running = self.handle_events()

            if self.current_screen == Screen.MENU:
                self.draw_menu()
            elif self.current_screen == Screen.MAP_VIEW:
                self.draw_map_view()
            elif self.current_screen == Screen.GAME:
                print("Vstup do GAME obrazovky...")
                if self.game:
                    print("Volám game.update(dt)...")
                    self.game.update(dt)
                print("Volám draw_ui...")
                self.draw_ui(horse)
                horse.update_animacia()


            # Limit FPS a dt pre update hry
            dt = clock.tick(60) / 1000

        pygame.quit()

