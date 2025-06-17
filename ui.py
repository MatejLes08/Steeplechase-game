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
    END_GAME = 5

class UI:
    def __init__(self, pridaj_callback=None, spomal_callback=None, koniec_callback=None, gamec=None, horse=None):
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
        self.neprejdenych = 2000
        self.aktualna_draha = ""
        self.stopky = "0:00.000"
        self.osobny_rekord = "N/A"
        self.pretazenie = 0
        self.final_time = None

        # Premenné pre meno hráča a vstupné pole
        self.meno_hraca = ""
        self.meno_input = ""
        self.input_rect = pygame.Rect(self.width // 2 - 150, 180, 300, 40)
        self.active_input = False

        # Tlačidlá v hre (zrušiť, spomaľ, pridať energiu, atď.)
        self.button_cancel = pygame.Rect(32, self.height - 80, 150, 50)
        self.button_decrease = pygame.Rect(216, self.height - 80, 150, 50)
        self.button_increase = pygame.Rect(400, self.height - 80, 150, 50)
        self.button_pause = pygame.Rect(584, self.height - 80, 150, 50)

        # Tlačidlá v hlavnom MENU
        self.button_start_menu = pygame.Rect(self.width // 2 - 100, 250, 200, 50)
        self.button_exit_menu = pygame.Rect(self.width // 2 - 100, 350, 200, 50)

        # Tlačidlá vo výbere mapy (MAP_VIEW)
        mid_x = self.width // 2
        self.button_play_map = pygame.Rect(mid_x + 70, 380, 120, 40)
        self.button_back_map = pygame.Rect(mid_x + 220, 380, 120, 40)

        # Nové tlačidlo pre server
        self.button_server = pygame.Rect(20, self.height - 70, 40, 40)

        # Tlačidlá pre prepínanie máp
        self.button_prev_map = pygame.Rect(mid_x + 140, 337, 60, 40)
        self.button_next_map = pygame.Rect(mid_x + 210, 337, 60, 40)
        self.selected_map_index = 0  # Index aktuálne vybranej mapy

        self.pridaj_callback = pridaj_callback
        self.spomal_callback = spomal_callback
        self.koniec_callback = koniec_callback

        # Cesta k obrázkom terénu z Game modulu
        self.draha = self.game.get_terrain_path() if self.game else []
        # Údaje pre rebríček (zatiaľ prázdne, budú načítané zo servera)
        self.scores = []  # list tupľov (poradie, meno, čas)
        self.my_score = None

        # Stav servera
        self.server_online = False
        self.server_url = "https://9cf54da1-84f4-45d0-b6fd-0817a0a4a654-00-2s3626w9v692a.janeway.replit.dev/"

        # Aktuálna obrazovka (štartujeme v MENU)
        self.current_screen = Screen.MENU

        # Tlačidlá pre vyskakovacie okná (relatívne k oknu 500x400)
        self.button_continue = pygame.Rect(175, 250, 150, 50)
        self.button_back_to_menu = pygame.Rect(175, 320, 150, 50)
        self.button_end_back_to_menu = pygame.Rect(175, 320, 150, 50)
        self.button_try_again = pygame.Rect(175, 250, 150, 50)

        self.audio_manager = AudioManager()

        #premenne pre pozadie
        self.dlzka_trate = len(self.draha) * self.game.sirka_useku

        self.bg_image_original = pygame.image.load("assets/pozadie.png").convert()
        self.scaled_bg_image = None  # bude sa vytvárať podľa veľkosti okna
        self.bg_image_width = 0
        self.update_scaled_background()


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

        # Načítanie rebríčka pre aktuálnu mapu
        map_json = self.biomes[self.selected_map_index]["map_json"]
        map_name = map_json.split('.')[0]
        y0 = 60
        if not self.scores or self.game.get_map_name() != map_name:
            # Načítanie nového rebríčka pre vybranú mapu
            try:
                response = requests.get(f"{Utils.SERVER_URL}/all-times?map={map_name}", timeout=2)
                if response.status_code == 200:
                    times = response.json().get("times", [])
                    # Zoradiť časy od najrýchlejšieho
                    sorted_times = sorted(times, key=Utils.extrahuj_cas_na_stotiny)
                    self.scores = [(i + 1, entry.get("name") or "Anonymný hráč", entry["time"]) for i, entry in
                                   enumerate(sorted_times)]
                    # Aktualizácia osobného rekordu
                    self.osobny_rekord = Utils.osobny_rekord(self.meno_hraca, map_name)
                    # Aktualizácia celkového rekordu
                    self.celkovy_rekord = Utils.najnizsi_cas(map_name)[0]
            except requests.RequestException:
                self.scores = []
                self.osobny_rekord = "N/A"
                self.celkovy_rekord = "N/A"

        if not self.scores or self.game.get_map_name() != map_name:
            # Načítanie nového rebríčka pre vybranú mapu
            try:
                response = requests.get(f"{Utils.SERVER_URL}/all-times?map={map_name}", timeout=2)
                if response.status_code == 200:
                    times = response.json().get("times", [])
                    # Zoradiť časy od najrýchlejšieho
                    sorted_times = sorted(times, key=Utils.extrahuj_cas_na_stotiny)
                    self.scores = [(i + 1, entry.get("name") or "Anonymný hráč", entry["time"]) for i, entry in
                                   enumerate(sorted_times)]
                    # Aktualizácia osobného rekordu
                    self.osobny_rekord = Utils.osobny_rekord(self.meno_hraca, map_name)
                    # Aktualizácia celkového rekordu
                    self.celkovy_rekord = Utils.najnizsi_cas(map_name)[0]
            except requests.RequestException:
                self.scores = []
                self.osobny_rekord = "N/A"
                self.celkovy_rekord = "N/A"

        if not self.scores:
            # Ak zatiaľ nemáme žiadne skóre, zobrazím placeholder text
            placeholder = self.font.render("Žiadne údaje", True, self.DARKGRAY)
            self.screen.blit(placeholder, (20, y0))
        else:
            # Vypíšem prvých 10 časov a mien
            for i, (rank, name, time_str) in enumerate(self.scores[:10]):
                txt = f"{rank}. {name}: {time_str}"
                self.screen.blit(self.font.render(txt, True, self.BLACK), (20, y0 + i * 30))


        # Zobrazenie osobného rekordu, posunuté nižšie pre väčší odstup
        osobny_text = f"Osobný rekord: {self.osobny_rekord}"
        self.screen.blit(self.font.render(osobny_text, True, self.BLACK), (20, y0 + 330))  # Changed from 300 to 330

        # Tlačidlo a stav servera
        pygame.draw.rect(self.screen, self.GRAY, self.button_server)
        self.render_button_text("->", self.button_server)
        if not self.server_online:
            offline_text = self.font.render("Offline", True, self.DARKGRAY)
            self.screen.blit(offline_text, (self.button_server.right + 10, self.height - 60))

        # --- pravá strana: podrobnosti mapy ---
        # Získanie názvu mapy cez volanie metódy
        lbl_map = self.font.render(map_name, True, self.BLACK)
        mx = half + (half - lbl_map.get_width()) // 2
        self.screen.blit(lbl_map, (mx, 20))

        # Obrázok mapy (pokúsim sa načítať, inak rámček)
        try:
            raw_img = pygame.image.load(self.biomes[self.selected_map_index]["map_image"]).convert()
            map_img = pygame.transform.scale(raw_img, (half - 40, 250))
            self.screen.blit(map_img, (half + 20, 60))
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
        # Vykreslí text na tlačidle, centrovaný v danom obdĺžniku
        lbl = self.font.render(text, True, self.BLACK)
        lbl_rect = lbl.get_rect(center=rect.center)
        self.screen.blit(lbl, lbl_rect)

    def set_selected_map(self):
        # Nastaví vybranú mapu v Game objekte
        selected_biome = self.biomes[self.selected_map_index]
        self.game.set_map(selected_biome["map_json"])
        # Aktualizuje dráhu pre novú mapu
        self.draha = self.game.get_terrain_path()

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

    def draw_energy(self, screen, font, value, x, y, width=150, height=30, green=(0, 255, 0), yellow=(255, 255, 0),
                    red=(255, 0, 0), black=(0, 0, 0)):

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

    def render_button_text(self, text, rect, color=(0, 0, 0), surface=None):
        if surface is None:
            surface = self.screen
        label = self.font.render(text, True, color)
        label_rect = label.get_rect(center=rect.center)
        surface.blit(label, label_rect)

    def draw_popup_window(self, content_callback):
        # Zastavenie vykresľovania hry, iba stmavnuté pozadie
        self.screen.fill(self.ORANGE)  # Základné pozadie
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Čierna s 50% priehľadnosťou
        self.screen.blit(overlay, (0, 0))

        # Vyskakovacie okno (500x400, centrované)
        popup_width, popup_height = 500, 400
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2
        popup_surface = pygame.Surface((popup_width, popup_height))
        popup_surface.fill(self.LIGHT_BLUE)

        # Volanie callbacku na vykreslenie obsahu okna
        content_callback(popup_surface, popup_x, popup_y)

        # Vykresli okno na obrazovku
        self.screen.blit(popup_surface, (popup_x, popup_y))
        pygame.display.flip()

    def draw_pause_screen(self):
        def draw_pause_content(surface, offset_x, offset_y):
            label = self.title_font.render("PAUZA", True, self.BLACK)
            surface.blit(label, ((500 - label.get_width()) // 2, 50))

            pygame.draw.rect(surface, self.GRAY, self.button_continue)
            self.render_button_text("Pokračovať", self.button_continue, surface=surface)

            pygame.draw.rect(surface, self.GRAY, self.button_back_to_menu)
            self.render_button_text("Späť do menu", self.button_back_to_menu, surface=surface)

        self.draw_popup_window(draw_pause_content)

    def draw_end_game_screen(self):
        def draw_end_content(surface, offset_x, offset_y):
            is_new_record = False
            if self.final_time and self.osobny_rekord != "N/A":
                final_stotiny = Utils.cas_na_stotiny(self.final_time)
                rekord_stotiny = Utils.cas_na_stotiny(self.osobny_rekord)
                is_new_record = final_stotiny <= rekord_stotiny

            title_text = "Nový rekord!" if is_new_record else "Dobehli ste do cieľa."
            title = self.title_font.render(title_text, True, self.BLACK)
            surface.blit(title, ((500 - title.get_width()) // 2, 50))

            time_text = f"Váš čas: {self.final_time}"
            time_label = self.font.render(time_text, True, self.BLACK)
            surface.blit(time_label, ((500 - time_label.get_width()) // 2, 120))

            rekord_text = f"Rekord: {self.osobny_rekord}"
            rekord_label = self.font.render(rekord_text, True, self.BLACK)
            surface.blit(rekord_label, ((500 - rekord_label.get_width()) // 2, 180))

            pygame.draw.rect(surface, self.GRAY, self.button_try_again)
            self.render_button_text("Skúsiť znova", self.button_try_again, surface=surface)

            pygame.draw.rect(surface, self.GRAY, self.button_end_back_to_menu)
            self.render_button_text("Späť do menu", self.button_end_back_to_menu, surface=surface)

        self.draw_popup_window(draw_end_content)

    def update_scaled_background(self):
        window_width, window_height = self.screen.get_size()
        scale_ratio = window_height / 324  # originálna výška obrázka
        new_width = int(1725 * scale_ratio)  # podľa originálu
        new_height = window_height
        self.bg_image_width = new_width
        self.scaled_bg_image = pygame.transform.scale(self.bg_image_original, (new_width, new_height))


    def draw_ui(self):
        if self.scaled_bg_image is None or self.screen.get_size()[1] != self.scaled_bg_image.get_height():
            self.update_scaled_background()

        # === POZADIE ===
        if self.scaled_bg_image:
            window_width, window_height = self.screen.get_size()

            
            scroll_x = (2000 - int((self.neprejdenych / 2000) * 2200))+220
            print(self.neprejdenych)
            self.screen.blit(
                self.scaled_bg_image,
                (0, 0),
                area=pygame.Rect(scroll_x, 0, window_width, window_height)
            )
        else:
            self.screen.fill((0, 0, 0))



            



        # --- ZÁKLADNÉ ROZMERY ---
        margin = 50
        icon_size = 50
        y_top = 50
        bar_w, bar_h = 200, 30
        x_center = self.width // 2
        x_right = self.width - margin

        # === ĽAVÝ STĽPEC ===
        bar_x = margin + icon_size + 40
        bar_y = y_top // 2 + 10

        # Energia (bar)
        pygame.draw.rect(self.screen, self.BLACK, (bar_x, bar_y, bar_w, bar_h), 4)
        stamina = self.energia
        bar_color = self.GREEN if stamina > 66 else self.YELLOW if stamina > 33 else self.RED
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, bar_w * (stamina / 100), bar_h))

        # Text percenta v strede baru
        stamina_text = f"{stamina}%"
        stamina_surf = self.font.render(stamina_text, True, self.BLACK)
        stamina_rect = stamina_surf.get_rect(center=(bar_x + bar_w // 2, bar_y + bar_h // 2))
        self.screen.blit(stamina_surf, stamina_rect)

        # Preťaženie vedľa baru
        pretazenie_text = f"{self.pretazenie}%/s"
        pretazenie_surf = self.font.render(pretazenie_text, True, self.BLACK)
        self.screen.blit(pretazenie_surf, (bar_x + bar_w + 20, bar_y))

        # Rýchlosť (pod barom)
        self.draw_text(self.screen, self.font, "Rýchlosť: ", f"{self.rychlost} km/h", margin, y_top + icon_size)

        # === STREDNÝ STĽPEC ===
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

        # === PRAVÝ STĽPEC ===
        # Čas
        self.cas = self.fontCas.render(self.stopky, True, self.BLACK)
        self.cas_rect = self.cas.get_rect(topright=(x_right, y_top - 30))
        self.screen.blit(self.cas, self.cas_rect)

        # Osobný rekord
        osobny_text = f"Osobný rekord: {self.osobny_rekord}"
        osobny_surf = self.font.render(osobny_text, True, self.BLACK)
        osobny_rect = osobny_surf.get_rect(topright=(x_right, y_top + 60))
        self.screen.blit(osobny_surf, osobny_rect)

        # Celkový rekord
        celkovy_text = f"Celkový rekord: {self.celkovy_rekord}"
        celkovy_surf = self.font.render(celkovy_text, True, self.BLACK)
        celkovy_rect = celkovy_surf.get_rect(topright=(x_right, y_top + 90))
        self.screen.blit(celkovy_surf, celkovy_rect)

        # === TLAČIDLO PAUZA (hore vľavo) ===
        pygame.draw.rect(self.screen, self.GRAY, self.button_pause)
        self.render_button_text("Pauza", self.button_pause)

        # === POSÚVAJÚCA SA CESTA ===
        if self.game:
            posun = self.game.posun_cesty
            sirka = self.game.sirka_useku
            self.offset = -int(posun % sirka)
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
        self.render_button_text("Zrušiť", self.button_cancel, color=self.BLACK)
        self.render_button_text("Spomaľ", self.button_decrease, color=self.BLACK)
        self.render_button_text("Pridaj", self.button_increase, color=self.BLACK)

        # === Hráč ===
        if self.horse:
            self.screen.blit(self.horse.current_image, (self.horse.position_x, self.horse.position_y))

        if self.game and self.game.running_game:
            self.horse.update_animacia()

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
                self.button_server = pygame.Rect(20, self.height - 70, 40, 40)
                self.button_prev_map = pygame.Rect(mid_x + 140, 337, 60, 40)
                self.button_next_map = pygame.Rect(mid_x + 210, 337, 60, 40)
                self.button_cancel = pygame.Rect(32, self.height - 80, 150, 50)
                self.button_decrease = pygame.Rect(216, self.height - 80, 150, 50)
                self.button_increase = pygame.Rect(400, self.height - 80, 150, 50)
                self.button_pause = pygame.Rect(584, self.height - 80, 150, 50)
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # MENU obrazovka: ovládanie inputu + tlačidiel
                popup_width, popup_height = 500, 400
                popup_x = (self.width - popup_width) // 2
                popup_y = (self.height - popup_height) // 2
                mouse_pos = event.pos
                relative_pos = (mouse_pos[0] - popup_x, mouse_pos[1] - popup_y)

                if self.current_screen == Screen.MENU:
                    self.active_input = self.input_rect.collidepoint(mouse_pos)
                    if self.button_start_menu.collidepoint(mouse_pos) and self.meno_input.strip():
                        self.meno_hraca = self.meno_input.strip()
                        # Zachované pre odosielanie mena
                        if self.game:
                            self.game.set_meno_hraca(self.meno_hraca)

                        # Načítanie rebríčka zo servera a kontrola stavu servera
                        map_json = self.biomes[self.selected_map_index]["map_json"]
                        map_name = map_json.split('.')[0]
                        try:
                            response = requests.get(f"{Utils.SERVER_URL}/all-times?map={map_name}", timeout=2)
                            if response.status_code == 200:
                                times = response.json().get("times", [])
                                # Zoradiť časy od najrýchlejšieho a filtrovať na najlepší čas pre každého hráča
                                best_times = {}
                                for entry in times:
                                    name = entry.get("name") or "Anonymný hráč"
                                    time_stotiny = Utils.extrahuj_cas_na_stotiny(entry)
                                    if name not in best_times or time_stotiny < Utils.extrahuj_cas_na_stotiny(
                                            {"time": best_times[name]["time"]}):
                                        best_times[name] = entry
                                sorted_times = sorted(best_times.values(), key=Utils.extrahuj_cas_na_stotiny)
                                # Vytvoriť zoznam tupľov (poradie, meno, čas)
                                self.scores = [(i + 1, entry.get("name") or "Anonymný hráč", entry["time"]) for i, entry
                                               in enumerate(sorted_times)]
                                # Nájdenie hráčovho skóre (ak existuje)
                                player_scores = [s for s in sorted_times if
                                                 s["name"].strip().lower() == self.meno_hraca.strip().lower()]
                                self.my_score = player_scores[0] if player_scores else None
                                self.osobny_rekord = player_scores[0]["time"] if player_scores else "N/A"
                                self.celkovy_rekord = Utils.najnizsi_cas(map_name)[0]
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
                            self.celkovy_rekord = "N/A"
                            self.server_online = False
                        self.current_screen = Screen.MAP_VIEW
                    elif self.button_exit_menu.collidepoint(mouse_pos):
                        return False
                    
                # MAP_VIEW obrazovka: prehľad mapy a tlačidlo servera
                elif self.current_screen == Screen.MAP_VIEW:
                    if self.button_play_map.collidepoint(mouse_pos):
                        if self.game:
                            # Nastaví vybranú mapu a prepne na hernú obrazovku
                            self.set_selected_map()
                        self.current_screen = Screen.GAME
                        self.audio_manager.start_music()  # Spusti hudbu pri prechode do hry
                    elif self.button_back_map.collidepoint(mouse_pos):
                        self.current_screen = Screen.MENU
                        self.reset()
                    elif self.button_server.collidepoint(mouse_pos) and self.server_online:
                        webbrowser.open(self.server_url)
                    elif self.button_prev_map.collidepoint(mouse_pos):
                        self.selected_map_index = (self.selected_map_index - 1) % len(self.biomes)
                    elif self.button_next_map.collidepoint(mouse_pos):
                        self.selected_map_index = (self.selected_map_index + 1) % len(self.biomes)

                # GAME obrazovka: pôvodné tlačidlá v hre
                elif self.current_screen == Screen.GAME:
                    if self.button_cancel.collidepoint(mouse_pos):
                        self.audio_manager.stop_music()
                        return False
                    elif self.button_decrease.collidepoint(mouse_pos) and self.spomal_callback:
                        self.spomal_callback()
                    elif self.button_increase.collidepoint(mouse_pos) and self.pridaj_callback:
                        self.pridaj_callback()
                    elif self.button_pause.collidepoint(mouse_pos):
                        self.current_screen = Screen.PAUSE
                        self.audio_manager.pause_music()
                elif self.current_screen == Screen.PAUSE:
                    if self.button_continue.collidepoint(relative_pos):
                        self.current_screen = Screen.GAME
                        self.audio_manager.unpause_music()
                    elif self.button_back_to_menu.collidepoint(relative_pos):
                        if self.restart_callback:
                            self.restart_callback()
                        self.audio_manager.stop_music()
                        self.current_screen = Screen.MENU
                        self.reset()
                elif self.current_screen == Screen.END_GAME:
                    if self.button_end_back_to_menu.collidepoint(relative_pos):
                        if self.restart_callback:
                            self.restart_callback()
                        self.audio_manager.stop_music()
                        self.current_screen = Screen.MENU
                        self.reset()
                    elif self.button_try_again.collidepoint(relative_pos):
                        if self.restart_callback:
                            self.restart_callback()  # Reštart hry
                            self.audio_manager.stop_music()
                            self.audio_manager.start_music()
                            self.game.running_game = True  # Obnovenie hry
                            self.current_screen = Screen.GAME
                            self.reset()

            # Spracovanie písania mena v MENU
            if event.type == pygame.KEYDOWN and self.current_screen == Screen.MENU and self.active_input:
                if event.key == pygame.K_RETURN and self.meno_input.strip():
                    self.meno_hraca = self.meno_input.strip()
                    # Zachované pre odosielanie mena
                    if self.game:
                        self.game.set_meno_hraca(self.meno_hraca)
                    # Načítanie rebríčka zo servera a kontrola stavu servera
                    map_json = self.biomes[self.selected_map_index]["map_json"]
                    map_name = map_json.split('.')[0]
                    try:
                        response = requests.get(f"{Utils.SERVER_URL}/all-times?map={map_name}", timeout=2)
                        if response.status_code == 200:
                            times = response.json().get("times", [])
                            # Zoradiť časy od najrýchlejšieho a filtrovať na najlepší čas pre každého hráča
                            best_times = {}
                            for entry in times:
                                name = entry.get("name") or "Anonymný hráč"
                                time_stotiny = Utils.extrahuj_cas_na_stotiny(entry)
                                if name not in best_times or time_stotiny < Utils.extrahuj_cas_na_stotiny(
                                        {"time": best_times[name]["time"]}):
                                    best_times[name] = entry
                            sorted_times = sorted(best_times.values(), key=Utils.extrahuj_cas_na_stotiny)
                            # Vytvoriť zoznam tupľov (poradie, meno, čas)
                            self.scores = [(i + 1, entry.get("name") or "Anonymný hráč", entry["time"]) for i, entry in
                                           enumerate(sorted_times)]
                            # Nájdenie hráčovho skóre (ak existuje)
                            player_scores = [s for s in sorted_times if
                                             s["name"].strip().lower() == self.meno_hraca.strip().lower()]
                            self.my_score = player_scores[0] if player_scores else None
                            self.osobny_rekord = player_scores[0]["time"] if player_scores else "N/A"
                            self.celkovy_rekord = Utils.najnizsi_cas(map_name)[0]
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
                        self.celkovy_rekord = "N/A"
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
        if self.game:
            self.draha = self.game.get_terrain_path()

    def update_record(self, cas, timestamp, osobny):
        # Aktualizuje osobný a celkový rekord na základe nového času a poskytnutého osobného rekordu
        if self.meno_hraca:
            print(
                f"[DEBUG] update_record: cas={cas}, osobny={osobny}, current_osobny={self.osobny_rekord}, celkovy={self.celkovy_rekord}")  # Debugging
            current_stotiny = Utils.cas_na_stotiny(cas)
            osobny_stotiny = Utils.cas_na_stotiny(osobny) if osobny != "N/A" else float('inf')
            celkovy_stotiny = Utils.cas_na_stotiny(self.celkovy_rekord) if self.celkovy_rekord != "N/A" else float(
                'inf')
            # Nastaví osobný rekord na poskytnutý osobný rekord alebo nový čas, ak je lepší
            if current_stotiny < osobny_stotiny:
                osobny_stotiny = Utils.cas_na_stotiny(osobny) if osobny != "N/A" else float('inf')
                celkovy_stotiny = Utils.cas_na_stotiny(self.celkovy_rekord) if self.celkovy_rekord != "N/A" else float('inf')
            # Nastaví osobný rekord na poskytnutý osobný rekord alebo nový čas, ak je lepší
            if current_stotiny < osobny_stotiny:
                self.osobny_rekord = cas
                print(f"[DEBUG] Updated osobny_rekord to new time: {cas}")
            else:
                self.osobny_rekord = osobny
                print(f"[DEBUG] Set osobny_rekord to provided osobny: {osobny}")
            # Aktualizuje celkový rekord, iba ak je nový čas lepší
            if current_stotiny < celkovy_stotiny:
                self.celkovy_rekord = cas
                print(f"[DEBUG] Updated celkovy_rekord to: {cas}")
            self.final_time = cas  # Uloženie finálneho času pre koncovú obrazovku

    def set_restart_callback(self, callback):
        self.restart_callback = callback

    def reset(self):
        self.rychlost = 0
        self.energia = 100
        self.neprejdenych = 2000
        self.stopky = "0:00.000"
        self.pretazenie = 0
        self.final_time = None
        if self.game:
            self.game.running_game = False
            self.draha = self.game.get_terrain_path()

    def zatvor(self):
        if self.game:
            self.game.running = False
        self.audio_manager.cleanup()
        pygame.quit()

    def run(self):
        # Hlavná slučka aplikácie
        clock = pygame.time.Clock()
        dt = 0.0
        if self.game:
            self.game.running = True

        while self.game and self.game.running:
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
            elif self.current_screen == Screen.PAUSE:
                self.draw_pause_screen()
            elif self.current_screen == Screen.END_GAME:
                self.draw_end_game_screen()

            # Limit FPS a dt pre update hry
            dt = clock.tick(60) / 1000

        # Uvoľnenie zdrojov pri ukončení
        self.audio_manager.cleanup()
        pygame.quit()