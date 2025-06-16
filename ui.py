import pygame
import requests
import webbrowser
from enum import Enum
from Utils import Utils
from Horse import Horse
from audio_manager import AudioManager  # Import AudioManager

# Enum pre jednotlivé obrazovky (MENU, výber mapy, samotná hra)
class Screen(Enum):
    MENU = 1
    MAP_VIEW = 2
    GAME = 3
    PAUSE = 4



class UI:
    def __init__(self, pridaj_callback, spomal_callback, koniec_callback, gamec, horse):
        # Inicializácia Pygame a uloženie referencie na hru (gamec)
        pygame.init()
        self.game = gamec
        self.horse = horse
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
        self.button_cancel = pygame.Rect(32, 700, 150, 50)
        self.button_decrease = pygame.Rect(216, 700, 150, 50)
        self.button_increase = pygame.Rect(416, 700, 150, 50)
        self.button_pause = pygame.Rect(620, 700, 150, 50)

        # Tlačidlá v hlavnom MENU
        self.button_start_menu = pygame.Rect(300, 250, 200, 50)
        self.button_exit_menu = pygame.Rect(300, 350, 200, 50)

        # Tlačidlá vo výbere mapy (MAP_VIEW)
        mid_x = self.width // 2
        self.button_play_map = pygame.Rect(mid_x + 70, 380, 120, 40)
        self.button_back_map = pygame.Rect(mid_x + 220, 380, 120, 40)
        # Nové tlačidlo pre server
        self.button_server = pygame.Rect(20, self.height - 70, 40, 40)
        # Tlačidlá pre prepínanie máp
        # Tlačidlá pre prepínanie máp
        self.button_prev_map = pygame.Rect(mid_x + 140, 337, 60, 40)
        self.button_next_map = pygame.Rect(mid_x + 210, 337, 60, 40)
        self.selected_map_index = 0  # Index aktuálne vybranej mapy

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
        self.server_url = "https://9cf54da1-84f4-45d0-b6fd-0817a0a4a654-00-2s3626w9v692a.janeway.replit.dev/"

        # Aktuálna obrazovka: štartujeme v MENU
        self.current_screen = Screen.MENU

        # Tlačidlá pre pauzu
        self.button_continue = pygame.Rect(self.width // 2 - 160, 200, 150, 50)
        self.button_back_to_menu = pygame.Rect(self.width // 2 + 10, 200, 150, 50)
        self.button_back_to_menu = pygame.Rect(self.width // 2 + 10, 200, 150, 50)

        # Inicializácia AudioManager
        self.audio_manager = AudioManager()


        # Mapovanie typu terénu na obrázok
        self.terrain_images = [
            pygame.image.load("assets/start.png").convert_alpha(),
            pygame.image.load("assets/cesta0.png").convert_alpha(),
            pygame.image.load("assets/cesta1.png").convert_alpha(),
            pygame.image.load("assets/cesta2.png").convert_alpha(),
            pygame.image.load("assets/narocne0.png").convert_alpha(),
            pygame.image.load("assets/narocne1.png").convert_alpha(),
            pygame.image.load("assets/narocne2.png").convert_alpha(),
            pygame.image.load("assets/sprinterske0.png").convert_alpha(),
            pygame.image.load("assets/sprinterske1.png").convert_alpha(),
            pygame.image.load("assets/sprinterske2.png").convert_alpha(),
            pygame.image.load("assets/napajadlo0.png").convert_alpha(),
            pygame.image.load("assets/napajadlo1.png").convert_alpha(),
            pygame.image.load("assets/napajadlo2.png").convert_alpha(),
            pygame.image.load("assets/ciel.png").convert_alpha(),
        ]
        

    def load_biomes(self):
        # Načítanie biomov s unikátnymi mapovými obrázkami a JSON súbormi
        return [
            {
                "name": "Les",
                "x_start": 0,
                "image": pygame.image.load("assets/cesta4_sideways.png").convert(),
                "decoration": pygame.image.load("assets/cesta4_sideways.png").convert_alpha(),
                "map_image": "assets/mapa1.png",
                "map_json": "mapa1.json"
            },
            {
                "name": "Púšť",
                "x_start": 1000,
                "image": pygame.image.load("assets/cesta4_sideways.png").convert(),
                "decoration": pygame.image.load("assets/cesta4_sideways.png").convert_alpha(),
                "map_image": "assets/mapa2.png",
                "map_json": "mapa2.json"
            },
            {
                "name": "Sneh",
                "x_start": 2000,
                "image": pygame.image.load("assets/cesta4_sideways.png").convert(),
                "decoration": pygame.image.load("assets/cesta4_sideways.png").convert_alpha(),
                "map_image": "assets/mapa3.jpg",
                "map_json": "mapa3.json"
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
            raw_img = pygame.image.load(self.biomes[self.selected_map_index]["map_image"]).convert()
            map_img = pygame.transform.scale(raw_img, (half - 40, 250))
            img_x = half + (half - map_img.get_width()) // 2
            self.screen.blit(map_img, (img_x, 60))
        except Exception as e:
            print(f"Error loading map image: {e}")
            pygame.draw.rect(self.screen, self.DARKGRAY, (half + 20, 60, half - 40, 250), 2)
            error_text = self.font.render("Obrázok mapy nenájdený", True, self.BLACK)
            self.screen.blit(error_text, (half + 30, 150))

        
        # Tlačidlá Hrať a Späť v pravom bloku, tlačidlá < a >
        pygame.draw.rect(self.screen, self.GRAY, self.button_prev_map)
        pygame.draw.rect(self.screen, self.GRAY, self.button_next_map)
        pygame.draw.rect(self.screen, self.GRAY, self.button_play_map)
        pygame.draw.rect(self.screen, self.GRAY, self.button_back_map)


        self.btn_text("<", self.button_prev_map)
        self.btn_text(">", self.button_next_map)

        self.btn_text("Hrať", self.button_play_map)
        self.btn_text("Späť", self.button_back_map)

        pygame.display.flip()

    def btn_text(self, text, rect):
        lbl = self.font.render(text, True, self.BLACK)
        lbl_rect = lbl.get_rect(center=rect.center)
        self.screen.blit(lbl, lbl_rect)

    def set_selected_map(self):
        # Nastaví vybranú mapu v Game objekte
        selected_biome = self.biomes[self.selected_map_index]
        self.game.set_map(selected_biome["map_json"])

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



    def draw_ui(self):
        self.screen.fill(self.ORANGE)

        # --- ZÁKLADNÉ ROZMERY ---
        margin = 50
        icon_size = 50
        y_top = 50
        bar_w, bar_h = 200, 30
        x_center = self.screen.get_width() // 2
        x_right = self.screen.get_width() - margin

        # === ĽAVÝ STĹPEC ===
        bar_x = margin + icon_size +40
        bar_y = y_top // 2 + 10

        # Energia (bar)
        pygame.draw.rect(self.screen, self.BLACK, (bar_x, bar_y, bar_w, bar_h), 4)
        stamina = self.energia
        bar_color = self.GREEN if stamina > 66 else self.YELLOW if stamina > 33 else self.RED
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, bar_w * stamina / 100, bar_h))

        # Text percenta v strede baru
        stamina_text = f"{stamina}%"
        stamina_surf = self.font.render(stamina_text, True, self.BLACK)
        stamina_rect = stamina_surf.get_rect(center=(bar_x + bar_w // 2, bar_y + bar_h - 12))
        self.screen.blit(stamina_surf, stamina_rect)

        # Preťaženie vedľa baru
        pretazenie_text = f"{self.pretazenie}%/s"
        pretazenie_surf = self.font.render(pretazenie_text, True, self.BLACK)
        self.screen.blit(pretazenie_surf, (bar_x + bar_w + 20, bar_y))

        # Rýchlosť (pod barom)
        self.draw_text(self.screen, self.font, "Rýchlosť: ", f"{self.rychlost} km/h", margin, y_top + icon_size)

        # === STREDNÝ STĹPEC ===
        # Prejdené metre
        metres_text = f"{self.neprejdenych} m"
        metres_surf = self.fontMetre.render(metres_text, True, self.BLACK)
        metres_rect = metres_surf.get_rect(center=(x_center, y_top))
        self.screen.blit(metres_surf, metres_rect)

        # Terén
        if self.game:
            self.aktualna_draha = self.game.get_akt_draha()
            
        terrain_text = f"{self.aktualna_draha}"
        terrain_surf = self.font.render(terrain_text, True, self.BLACK)
        terrain_rect = terrain_surf.get_rect(center=(x_center, y_top + 50))
        self.screen.blit(terrain_surf, terrain_rect)

        # === PRAVÝ STĹPEC ===
        # Čas
        self.cas = self.fontCas.render(self.stopky, True, self.BLACK)
        self.cas_rect = self.cas.get_rect(topright=(x_right, y_top - 30))
        self.screen.blit(self.cas, self.cas_rect)

        # Rekord
        rekord_text = f"Rekord: {self.osobny_rekord}"
        rekord_surf = self.font.render(rekord_text, True, self.BLACK)
        rekord_rect = rekord_surf.get_rect(topright=(x_right, y_top + 60))
        self.screen.blit(rekord_surf, rekord_rect)

        # === TLAČIDLO PAUZA (hore vľavo) ===
        pygame.draw.rect(self.screen, self.GRAY, self.button_pause)
        self.render_button_text(self.screen, self.font, "Pauza", self.button_pause)

        # === POSÚVAJÚCA SA CESTA ===
        if self.game:
            posun = self.game.posun_cesty
            sirka = self.game.sirka_useku
            self.offset = -int(posun % sirka)
            start_meter = int(posun // sirka)
            terrain_map = self.draha  # zoznam indexov obrázkov (1–13, vrátane)
            start_meter = int(posun // sirka)
            terrain_map = self.draha  # zoznam indexov obrázkov (1–13, vrátane)

            for i in range(30):
                meter_index = start_meter + i
                if 0 <= meter_index < len(terrain_map):
                    image_index = terrain_map[meter_index]
                    if 0 <= image_index < len(self.terrain_images):
                        image = self.terrain_images[image_index]
                        x_pozicia = i * sirka + self.offset
                        img_scaled = pygame.transform.scale(image, (sirka, 200))
                        self.screen.blit(img_scaled, (x_pozicia, 400))

        # === TLAČIDLÁ ===
        pygame.draw.rect(self.screen, self.RED, self.button_cancel)
        pygame.draw.rect(self.screen, self.GRAY, self.button_decrease)
        pygame.draw.rect(self.screen, self.GRAY, self.button_increase)
        self.render_button_text(self.screen, self.font, "Zrušiť", self.button_cancel, color=self.BLACK)
        self.render_button_text(self.screen, self.font, "Spomaľ", self.button_decrease, color=self.BLACK)
        self.render_button_text(self.screen, self.font, "Pridaj", self.button_increase, color=self.BLACK)

        # === Hráč ===
        self.screen.blit(self.horse.current_image, (self.horse.position_x, self.horse.position_y))

        pygame.display.flip()



    def handle_events(self):
        # Spracovanie udalostí (klávesy, myš)
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.input_rect = pygame.Rect(self.width // 2 - 150, 180, 300, 40)
                self.button_start_menu = pygame.Rect(self.width // 2 - 100, 250, 200, 50)
                self.button_exit_menu = pygame.Rect(self.width // 2 - 100, 350, 200, 50)
                mid_x = self.width // 2
                self.button_play_map = pygame.Rect(mid_x + 70, 380, 120, 40)
                self.button_back_map = pygame.Rect(mid_x + 220, 380, 120, 40)
                self.button_prev_map = pygame.Rect(mid_x + 140, 337, 60, 40)
                self.button_next_map = pygame.Rect(mid_x + 210, 337, 60, 40)
                self.button_server = pygame.Rect(20, self.height - 70, 40, 40)
                self.button_continue = pygame.Rect(self.width // 2 - 160, 200, 150, 50)
                self.button_back_to_menu = pygame.Rect(self.width // 2 + 10, 200, 150, 50)
                self.button_back_to_menu = pygame.Rect(self.width // 2 + 10, 200, 150, 50)
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
                        # Nastaví vybranú mapu a prepne na hernú obrazovku
                        self.set_selected_map()
                        # Nastaví vybranú mapu a prepne na hernú obrazovku
                        self.set_selected_map()
                        self.current_screen = Screen.GAME
                        self.audio_manager.start_music()  # Spusti hudbu pri prechode do hry
                    elif self.button_back_map.collidepoint(event.pos):
                        self.current_screen = Screen.MENU
                    elif self.button_server.collidepoint(event.pos) and self.server_online:
                        webbrowser.open(self.server_url)
                    elif self.button_prev_map.collidepoint(event.pos):
                        self.selected_map_index = (self.selected_map_index - 1) % len(self.biomes)
                    elif self.button_next_map.collidepoint(event.pos):
                        self.selected_map_index = (self.selected_map_index + 1) % len(self.biomes)


                # GAME obrazovka: pôvodné tlačidlá v hre
                elif self.current_screen == Screen.GAME:
                    if self.button_cancel.collidepoint(event.pos):
                        self.audio_manager.stop_music()
                        return False
                    elif self.button_decrease.collidepoint(event.pos):
                        self.spomal_callback()
                    elif self.button_increase.collidepoint(event.pos):
                        self.pridaj_callback()
                    elif self.button_pause.collidepoint(event.pos):
                        self.current_screen = Screen.PAUSE
                        self.audio_manager.pause_music()
                elif self.current_screen == Screen.PAUSE:
                    if self.button_continue.collidepoint(event.pos):
                        self.current_screen = Screen.GAME
                        self.audio_manager.unpause_music()
                    elif self.button_back_to_menu.collidepoint(event.pos):
                        if self.restart_callback:
                            self.restart_callback()
                        self.audio_manager.stop_music()
                        self.current_screen = Screen.MENU
                        
                        


            # Spracovanie písania mena v MENU
            if event.type == pygame.KEYDOWN and self.current_screen == Screen.MENU and self.active_input:
                if event.key == pygame.K_RETURN and self.meno_plan.strip():
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
                                    name = entry.get("name") or "Anonymný hráč"
                                    name = entry.get("name") or "Anonymný hráč"
                                    time_stotiny = Utils.extrahuj_cas_na_stotiny(entry)
                                    if name not in times or time_stotiny < Utils.extrahuj_cas_na_stotiny({"time": best_times[name]["time"]}):
                                        best_times[name] = entry
                                sorted_times = sorted(best_times.values(), key=Utils.extrahuj_cas_na_stotiny)
                                # Vytvoriť zoznam tupľov (poradie, meno, čas)
                                self.scores = [(i + 1, entry.get("name") or "Anonymný hráč", entry["time"]) for i, entry in enumerate(sorted_times)]
                                self.scores = [(i + 1, entry.get("name") or "Anonymný hráč", entry["time"]) for i, entry in enumerate(sorted_times)]
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
                    except Exception:
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

    def set_restart_callback(self, callback):
        self.restart_callback = callback


    def reset(self, horse, game, pridaj, spomal, koniec, update_ui, update_record):
        self.horse = horse
        self.game = game
        self.pridaj_callback = pridaj
        self.spomal_callback = spomal
        self.koniec_callback = koniec
        self.rekord = Utils.najnizsi_cas()[0] if isinstance(Utils.najnizsi_cas(), tuple) else Utils.najnizsi_cas()
        self.stopky = "0:00.000"
        self.energia = 100
        self.rychlost = 0
        self.neprejdenych = 0
        self.pretaz = 0
        self.pretaz = 0
        self.game.update_ui = update_ui
        self.game.update_record = update_record



    def run(self):
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
                self.draw_ui()
                self.horse.update_animacia()
            elif self.current_screen == Screen.PAUSE:
                self.draw_pause_screen()


            # Limit FPS a dt pre update hry
            dt = clock.tick(60) / 1000

        # Uvoľnenie zdrojov pri ukončení
        self.audio_manager.cleanup()
        pygame.quit()