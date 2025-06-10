import pygame
import requests
import webbrowser
from enum import Enum
from Utils import Utils
from Horse import Horse


# Enum pre jednotlivé obrazovky (MENU, výber mapy, samotná hra)
class Screen(Enum):
    MENU = 1
    MAP_VIEW = 2
    GAME = 3
    PAUSE = 4



class UI:
    def __init__(self, pridaj_callback, spomal_callback, koniec_callback, gamec):
        # Inicializácia Pygame a uloženie referencie na hru (gamec)
        pygame.init()
        self.game = gamec
        # Rozmer okna hry
        self.width = 820
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Steeplchase preteky")

        # Fonty na rôzne časti UI
        self.title_font = pygame.font.SysFont(None, 60)
        self.font = pygame.font.SysFont(None, 40)
        self.fontMetre = pygame.font.SysFont(None, 110)
        self.fontCas = pygame.font.SysFont("Arial", 70)

        self.biomes = self.load_biomes()

        # Definícia farieb v RGB
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.DARKGRAY = (100, 100, 100)
        self.BLACK = (0, 0, 0)
        self.ORANGE = (57, 183, 177)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.LIGHT_BLUE = (173, 216, 230)

        # Herné premenné (rýchlosť, energia, prejdená vzdialenosť, atď.)
        self.rychlost = 0
        self.energia = 100
        self.neprejdenych = 0
        self.aktualna_draha = ""
        self.stopky = "0:00:00"
        self.osobny_rekord = "N/A"  # Initialize personal best
        self.pretazenie = 0

        # Premenné pre meno hráča a vstupné pole
        self.meno_hraca = ""
        self.meno_input = ""
        self.input_rect = pygame.Rect(self.width // 2 - 150, 180, 300, 40)
        self.active_input = False

        # Tlačidlá v hre (zrušiť, spomaľ, pridať energiu, atď.)
        self.button_cancel = pygame.Rect(32, 433, 150, 50)
        self.button_decrease = pygame.Rect(216, 433, 150, 50)
        self.button_increase = pygame.Rect(416, 433, 150, 50)
        self.button_pause = pygame.Rect(620, 433, 150, 50)

        # Tlačidlá v hlavnom MENU
        self.button_start_menu = pygame.Rect(300, 250, 200, 50)
        self.button_exit_menu = pygame.Rect(300, 350, 200, 50)

        # Tlačidlá vo výbere mapy (MAP_VIEW)
        mid_x = self.width // 2
        self.button_play_map = pygame.Rect(mid_x + 70, 380, 120, 40)
        self.button_back_map = pygame.Rect(mid_x + 220, 380, 120, 40)
        # Nové tlačidlo pre server
        self.button_server = pygame.Rect(20, self.height - 70, 40, 40)

        # Callback funkcie pre volanie od Game logiky
        self.pridaj_callback = pridaj_callback
        self.spomal_callback = spomal_callback
        self.koniec_callback = koniec_callback

        # Cesta k obrázkom terénu z Game modulu
        self.draha = self.game.get_terrain_path()
        # Údaje pre rebríček (zatiaľ prázdne, budú načítané zo servera)
        self.scores = []  # list tupľov (poradie, meno, čas)
        self.my_score = None
        # Stav servera
        self.server_online = False
        self.server_url = "https://9cf54da1-84f4-45d0-b6fd-0817a0a4a654-00-2s3626w9v692a.janeway.replit.dev/"

        # Aktuálna obrazovka (štartujeme v MENU)
        self.current_screen = Screen.MENU

        # Tlačidlá pre pauzu
        self.button_continue = pygame.Rect(self.width // 2 - 160, 200, 150, 50)
        self.button_back_to_menu = pygame.Rect(self.width // 2 + 10, 200, 150, 50)


    def load_biomes(self):
        return [
            {
                "name": "Les",
                "x_start": 0,
                "image": pygame.image.load("assets/cesta4_sideways.png").convert(),
                "decoration": pygame.image.load("assets/cesta4_sideways.png").convert_alpha()
            },
            {
                "name": "Púšť",
                "x_start": 1000,
                "image": pygame.image.load("assets/cesta4_sideways.png").convert(),
                "decoration": pygame.image.load("assets/cesta4_sideways.png").convert_alpha()
            },
            {
                "name": "Sneh",
                "x_start": 2000,
                "image": pygame.image.load("assets/cesta4_sideways.png").convert(),
                "decoration": pygame.image.load("assets/cesta4_sideways.png").convert_alpha()
            }
        ]

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
          - ľavá: rebríček s top 10 časmi a menami zo servera
          - pravá: podrobnosti mapy (názov, obrázok, tlačidlá)
        """
        self.screen.fill(self.ORANGE)
        half = self.width // 2
        # Farby pre pozadie blokov
        pygame.draw.rect(self.screen, self.ORANGE, (0, 0, half, self.height))
        pygame.draw.rect(self.screen, self.ORANGE, (half, 0, half, self.height))

        # --- ľavá strana: rebríček ---
        # Vykreslenie názvu "Rebríček" vycentrovaného v ľavom bloku
        title_surf = self.title_font.render("Rebríček", True, self.BLACK)
        # x-ová pozícia = stred bloku minus polovica šírky textu
        x_center = (half // 2) - (title_surf.get_width() // 2)
        self.screen.blit(title_surf, (x_center, 10))

        y0 = 60
        if not self.scores:
            # Ak zatiaľ nemáme žiadne skóre, zobrazím placeholder text
            placeholder = self.font.render("Žiadne údaje", True, self.DARKGRAY)
            self.screen.blit(placeholder, (20, y0))
        else:
            # Vypíšem prvých 10 časov a mien
            for i, (rank, name, time_str) in enumerate(self.scores[:10]):
                txt = f"{rank}. {name}: {time_str}"
                self.screen.blit(self.font.render(txt, True, self.BLACK), (20, y0 + i * 30))

        # Tlačidlo a stav servera
        pygame.draw.rect(self.screen, self.GRAY, self.button_server)
        self.render_button_text(self.screen, self.font, "->", self.button_server)
        if not self.server_online:
            offline_text = self.font.render("Stránka je offline", True, self.DARKGRAY)
            self.screen.blit(offline_text, (self.button_server.right + 10, self.height - 60))

        # --- pravá strana: podrobnosti mapy ---
        # Získanie názvu mapy cez volanie metódy (fallback na "MAPA")
        map_name = getattr(self.game, 'get_map_name', lambda: "MAPA")()
        lbl_map = self.font.render(map_name, True, self.BLACK)
        mx = half + (half - lbl_map.get_width()) // 2
        self.screen.blit(lbl_map, (mx, 20))

        # Obrázok mapy (pokúsim sa načítať, inak rámček)
        try:
            raw_img = pygame.image.load(self.draha).convert()
            map_img = pygame.transform.scale(raw_img, (half - 40, 250))
            self.screen.blit(map_img, (half + 20, 60))
        except Exception:
            pygame.draw.rect(self.screen, self.DARKGRAY, (half + 20, 60, half - 40, 250), 2)

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

    def draw_energy(self, screen, font, value, x, y, width=150, height=30, green=(0, 255, 0), yellow=(255, 255, 0), red=(255, 0, 0), black=(0, 0, 0)):
        # Funkcia na vykreslenie obdĺžnika s energiou
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

    def draw_pause_screen(self):
        self.screen.fill(self.LIGHT_BLUE)
        label = self.title_font.render("PAUZA", True, self.BLACK)
        self.screen.blit(label, (self.width // 2 - label.get_width() // 2, 100))

        pygame.draw.rect(self.screen, self.GRAY, self.button_continue)
        self.render_button_text(self.screen, self.font, "Pokračovať", self.button_continue)

        pygame.draw.rect(self.screen, self.GRAY, self.button_back_to_menu)
        self.render_button_text(self.screen, self.font, "Späť do menu", self.button_back_to_menu)

        pygame.display.flip()



    def draw_ui(self, horse):
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

        self.draw_text(self.screen, self.font, "Rekord", self.osobny_rekord, 580, 70)  # Display personal best as "Rekord"
        self.draw_text(self.screen, self.font, "Preťaženie", self.pretazenie, 580, 110)

        pygame.draw.rect(self.screen, self.GRAY, self.button_pause)
        self.render_button_text(self.screen, self.font, "Pauza", self.button_pause)

        # Posúvajúce sa pásy (cesta)
        if self.game:
            posun = self.game.posun_cesty
            sirka = self.game.sirka_useku
            self.offset = -int(posun % sirka)
            start_index = int(posun // sirka) - 1
            world_x = posun

            for i in range(15):
                x_pozicia = i * sirka + self.offset
                current_world_x = world_x + i * sirka
                # Získanie obrázkov a prechodovej hodnoty
                img1, img2, decor1, decor2, t = self.get_biome_images(current_world_x)
                # Povrch pre blendovanie
                blended_surface = pygame.Surface((sirka, 200), pygame.SRCALPHA)
                img1_scaled = pygame.transform.scale(img1, (sirka, 200))
                img2_scaled = pygame.transform.scale(img2, (sirka, 200))
                img1_scaled.set_alpha(int(255 * (1 - t)))
                img2_scaled.set_alpha(int(255 * t))
                blended_surface.blit(img1_scaled, (0, 0))
                blended_surface.blit(img2_scaled, (0, 0))
                self.screen.blit(blended_surface, (x_pozicia, 220))
                # Dekorácie
                decor_blend = pygame.Surface((sirka, 200), pygame.SRCALPHA)
                decor1_scaled = pygame.transform.scale(decor1, (sirka, 200))
                decor2_scaled = pygame.transform.scale(decor2, (sirka, 200))
                decor1_scaled.set_alpha(int(255 * (1 - t)))
                decor2_scaled.set_alpha(int(255 * t))
                decor_blend.blit(decor1_scaled, (0, 0))
                decor_blend.blit(decor2_scaled, (0, 0))
                self.screen.blit(decor_blend, (x_pozicia, 220))

        # Tlačidlá
        pygame.draw.rect(self.screen, self.RED, self.button_cancel)
        pygame.draw.rect(self.screen, self.GRAY, self.button_decrease)
        pygame.draw.rect(self.screen, self.GRAY, self.button_increase)
        self.render_button_text(self.screen, self.font, "Zrušiť", self.button_cancel, color=self.BLACK)
        self.render_button_text(self.screen, self.font, "Spomaľ", self.button_decrease, color=self.BLACK)
        self.render_button_text(self.screen, self.font, "Pridaj", self.button_increase, color=self.BLACK)
        # vykreslenie obrazku hráča
        self.screen.blit(horse.current_image, (horse.position_x, horse.position_y))
        pygame.display.flip()

    def handle_events(self):
        # Spracovanie udalostí (klávesy, myš)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # MENU obrazovka: ovládanie inputu + tlačidiel
                if self.current_screen == Screen.MENU:
                    self.active_input = self.input_rect.collidepoint(event.pos)
                    if self.button_start_menu.collidepoint(event.pos) and self.meno_input.strip():
                        self.meno_hraca = self.meno_input.strip()
                        # Zachované pre odosielanie mena
                        self.game.set_meno_hraca(self.meno_hraca)
                        # Načítanie rebríčka zo servera a kontrola stavu servera
                        try:
                            response = requests.get(f"{Utils.SERVER_URL}/all-times", timeout=2)
                            if response.status_code == 200:
                                try:
                                    times = response.json().get("times", [])
                                    # Zoradiť časy od najrýchlejšieho a filtrovať na najlepší čas pre každého hráča
                                    best_times = {}
                                    for entry in times:
                                        name = entry["name"] or "Anonymný hráč"
                                        time_stotiny = Utils.extrahuj_cas_na_stotiny(entry)
                                        if name not in best_times or time_stotiny < Utils.extrahuj_cas_na_stotiny({"time": best_times[name]["time"]}):
                                            best_times[name] = entry
                                    sorted_times = sorted(best_times.values(), key=Utils.extrahuj_cas_na_stotiny)
                                    # Vytvoriť zoznam tupľov (poradie, meno, čas)
                                    self.scores = [(i + 1, entry["name"] or "Anonymný hráč", entry["time"]) for i, entry in enumerate(sorted_times)]
                                    # Nájdenie hráčovho skóre (ak existuje)
                                    player_scores = [s for s in sorted_times if s["name"].strip().lower() == self.meno_hraca.strip().lower()]
                                    self.my_score = player_scores[0] if player_scores else None
                                    self.osobny_rekord = player_scores[0]["time"] if player_scores else "N/A"  # Set personal best
                                except (ValueError, KeyError):
                                    self.scores = []
                                    self.my_score = None
                                    self.osobny_rekord = "N/A"
                            # Kontrola stavu servera
                            try:
                                server_response = requests.get(self.server_url, timeout=2)
                                self.server_online = server_response.status_code == 200
                            except requests.RequestException:
                                self.server_online = False
                        except requests.RequestException:
                            self.scores = []
                            self.my_score = None
                            self.osobny_rekord = "N/A"
                            self.server_online = False
                        self.current_screen = Screen.MAP_VIEW
                    elif self.button_exit_menu.collidepoint(event.pos):
                        return False
                # MAP_VIEW obrazovka: prehľad mapy a tlačidlo servera
                elif self.current_screen == Screen.MAP_VIEW:
                    if self.button_play_map.collidepoint(event.pos):
                        # Prepne len obrazovku, hra sa spustí v draw_ui/Game logike
                        self.current_screen = Screen.GAME
                    elif self.button_back_map.collidepoint(event.pos):
                        self.current_screen = Screen.MENU
                    elif self.button_server.collidepoint(event.pos) and self.server_online:
                        webbrowser.open(self.server_url)
                # GAME obrazovka: pôvodné tlačidlá v hre
                elif self.current_screen == Screen.GAME:
                    if self.button_cancel.collidepoint(event.pos):
                        return False
                    elif self.button_decrease.collidepoint(event.pos):
                        self.spomal_callback()
                    elif self.button_increase.collidepoint(event.pos):
                        self.pridaj_callback()
                    elif self.button_pause.collidepoint(event.pos):
                        self.current_screen = Screen.PAUSE
                elif self.current_screen == Screen.PAUSE:
                    if self.button_continue.collidepoint(event.pos):
                        self.current_screen = Screen.GAME
                    elif self.button_back_to_menu.collidepoint(event.pos):
                        self.current_screen = Screen.MENU


            # Spracovanie písania mena v MENU
            if event.type == pygame.KEYDOWN and self.current_screen == Screen.MENU and self.active_input:
                if event.key == pygame.K_RETURN and self.meno_input.strip():
                    self.meno_hraca = self.meno_input.strip()
                    # Zachované pre odosielanie mena
                    self.game.set_meno_hraca(self.meno_hraca)
                    # Načítanie rebríčka zo servera a kontrola stavu servera
                    try:
                        response = requests.get(f"{Utils.SERVER_URL}/all-times", timeout=2)
                        if response.status_code == 200:
                            try:
                                times = response.json().get("times", [])
                                # Zoradiť časy od najrýchlejšieho a filtrovať na najlepší čas pre každého hráča
                                best_times = {}
                                for entry in times:
                                    name = entry["name"] or "Anonymný hráč"
                                    time_stotiny = Utils.extrahuj_cas_na_stotiny(entry)
                                    if name not in best_times or time_stotiny < Utils.extrahuj_cas_na_stotiny({"time": best_times[name]["time"]}):
                                        best_times[name] = entry
                                sorted_times = sorted(best_times.values(), key=Utils.extrahuj_cas_na_stotiny)
                                # Vytvoriť zoznam tupľov (poradie, meno, čas)
                                self.scores = [(i + 1, entry["name"] or "Anonymný hráč", entry["time"]) for i, entry in enumerate(sorted_times)]
                                # Nájdenie hráčovho skóre (ak existuje)
                                player_scores = [s for s in sorted_times if s["name"].strip().lower() == self.meno_hraca.strip().lower()]
                                self.my_score = player_scores[0] if player_scores else None
                                self.osobny_rekord = player_scores[0]["time"] if player_scores else "N/A"  # Set personal best
                            except (ValueError, KeyError):
                                self.scores = []
                                self.my_score = None
                                self.osobny_rekord = "N/A"
                        # Kontrola stavu servera
                        try:
                            server_response = requests.get(self.server_url, timeout=2)
                            self.server_online = server_response.status_code == 200
                        except requests.RequestException:
                            self.server_online = False
                    except requests.RequestException:
                        self.scores = []
                        self.my_score = None
                        self.osobny_rekord = "N/A"
                        self.server_online = False
                    self.current_screen = Screen.MAP_VIEW
                elif event.key == pygame.K_BACKSPACE:
                    self.meno_input = self.meno_input[:-1]
                elif len(self.meno_input) < 20:
                    self.meno_input += event.unicode

        return True

    def set_game(self, game):
        # Umožňuje neskôr zmeniť referenciu na game objekt
        self.game = game

    def update_record(self, cas, timestamp):
        # Aktualizuje osobný rekord ak je nový čas lepší
        if self.meno_hraca:
            current_stotiny = Utils.cas_na_stotiny(cas)
            best_stotiny = Utils.cas_na_stotiny(self.osobny_rekord) if self.osobny_rekord != "N/A" else float('inf')
            if current_stotiny < best_stotiny:
                self.osobny_rekord = cas

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
                # Tu sa vykreslí samotná hra pomocou draw_ui (a horse animácie)
                if self.game:
                    self.game.update(dt)
                self.draw_ui(horse)
                horse.update_animacia()
            elif self.current_screen == Screen.PAUSE:
                self.draw_pause_screen()


            # Limit FPS a dt pre update hry
            dt = clock.tick(60) / 1000

        pygame.quit()