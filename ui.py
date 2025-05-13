import pygame
from enum import Enum
from Utils import Utils
from Horse import Horse

# Enum pre jednotlivé obrazovky (MENU, výber mapy, samotná hra)
class Screen(Enum):
    MENU = 1
    MAP_VIEW = 2
    GAME = 3

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

        # Definícia farieb v RGB
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.DARKGRAY = (100, 100, 100)
        self.BLACK = (0, 0, 0)
        self.ORANGE = (255, 198, 111)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)

        # Herné premenné (rýchlosť, energia, prejdená vzdialenosť, atď.)
        self.rychlost = 0
        self.energia = 100
        self.neprejdenych = 0
        self.aktualna_draha = ""
        self.stopky = "0:00:00"
        self.rekord = Utils.najnizsi_cas()
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

        # Tlačidlá v hlavnom MENU
        self.button_start_menu = pygame.Rect(300, 250, 200, 50)
        self.button_exit_menu = pygame.Rect(300, 350, 200, 50)

        # Tlačidlá vo výbere mapy (MAP_VIEW)
        mid_x = self.width // 2
        self.button_play_map = pygame.Rect(mid_x + 70, 380, 120, 40)
        self.button_back_map = pygame.Rect(mid_x + 220, 380, 120, 40)

        # Callback funkcie pre volanie od Game logiky
        self.pridaj_callback = pridaj_callback
        self.spomal_callback = spomal_callback
        self.koniec_callback = koniec_callback

        # Cesta k obrázkom terénu z Game modulu
        self.draha = self.game.get_terrain_path()

        # Údaje pre rebríček (zatiaľ prázdne, fallbacky neskôr)
        self.scores = []      # list tupľov (poradie, meno, čas)
        self.my_score = None

        # Aktuálna obrazovka (štartujeme v MENU)
        self.current_screen = Screen.MENU

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

    def draw_ui(self, horse):
        self.screen.fill(self.ORANGE)

        

        #Fukcia na vykreslenie obdlznika s energiou
        def draw_energy(value, x, y, width=150, height=30):
            # Uistíme sa, že hodnota je medzi 0 a 100
            value = max(0, min(100, value))
            
            # Vypočítaj šírku "plného" baru
            bar_width = int((value / 100) * width)

            # Vyber farbu podľa hodnoty
            if value > 66:
                bar_color = self.GREEN      # zelená
            elif value > 33:
                bar_color = self.YELLOW    # oranžová
            else:
                bar_color = self.RED      # červená

            # Podkladový rám
            rect_bg = pygame.Rect(x, y, width, height)
            pygame.draw.rect(self.screen, (150, 150, 150), rect_bg)              # tmavý podklad
            pygame.draw.rect(self.screen, self.BLACK, rect_bg, 2)        # rám

            # Plniaci sa bar
            rect_fill = pygame.Rect(x, y, bar_width, height)
            pygame.draw.rect(self.screen, bar_color, rect_fill)

            # Text do stredu (napr. "82%")
            text = self.font.render(f"{value}%", True, self.BLACK)
            text_rect = text.get_rect(center=rect_bg.center)
            self.screen.blit(text, text_rect)


        # Funkcia na vykreslenie štítku + hodnoty
        def draw_text(label, value, x, y):
            text = self.font.render(f"{label}: {value}", True, self.BLACK)
            self.screen.blit(text, (x, y))

        # Zobrazenie herných údajov
        draw_text("Rýchlosť", self.rychlost, 20, 60)
        draw_energy(self.energia, 91, 20)
        #zobrazovanie textu metrov v strede hore
        self.metre = self.fontMetre.render(str(self.neprejdenych)+"m", True,  self.BLACK)
        #zarovnanie textu na stred šírky obrazovky
        self.metre_rect = self.metre.get_rect(center=(self.screen.get_width() // 2, 40))
        self.screen.blit(self.metre, self.metre_rect)

        draw_text("Terén", self.aktualna_draha, 20, 100)
        if self.game:
            self.aktualna_draha = self.game.get_akt_draha()
        draw_text("Terén", self.aktualna_draha, 20, 100)


        #zobrazovanie casu
        self.cas = self.fontCas.render(self.stopky, True,  self.BLACK)
        self.cas_rect = self.cas.get_rect(center=(700, 40))
        self.screen.blit(self.cas, self.cas_rect)
        draw_text("Rekord", self.rekord, 580, 70)
        draw_text("Preťaženie", self.pretazenie, 580, 110)
      
             # Posúvajúce sa pásy (cesta)
        if self.game:
            posun = self.game.posun_cesty
            sirka = self.game.sirka_useku
            draha = self.draha
            self.offset = -int(posun % sirka)
            start_index = int(posun // sirka)-9

            for i in range(15):
                index = start_index + i
                if index >= len(draha):
                    break
                nazov_terenu = draha[index]

                farba = {
                    "Cesta": (160, 82, 45),
                    "Napájadlo": (0, 191, 255),
                    "Náročné pásmo": (139, 0, 0),
                    "Šprintérske pásmo": (255, 215, 0),
                }.get(nazov_terenu, (100, 100, 100))

                x_pozicia = i * sirka + self.offset
                rect = pygame.Rect(x_pozicia, 220, sirka, 200)

                pygame.draw.rect(self.screen, farba, rect)           # výplň
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)     # čierny okraj



        # Tlačidlá
        pygame.draw.rect(self.screen, self.RED, self.button_cancel)
        pygame.draw.rect(self.screen, self.GRAY, self.button_decrease)
        pygame.draw.rect(self.screen, self.GRAY, self.button_increase)
        

        # Texty na tlačidlách
        def render_button_text(text, rect):
            label = self.font.render(text, True, self.BLACK)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

        render_button_text("Zrušiť", self.button_cancel)
        render_button_text("Spomaľ", self.button_decrease)
        render_button_text("Pridaj", self.button_increase)
        

        #vykreslenie obrazku hráča
        self.screen.blit(horse.current_image, (horse.position_x, horse.position_y))

        # Aktualizácia obrazovky
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

    def set_game(self, game):
        # Umožňuje neskôr zmeniť referenciu na game objekt
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
                # Tu sa vykreslí samotná hra pomocou draw_ui (a horse animácie)
                if self.game:
                    self.game.update(dt)
                self.draw_ui(horse)
                horse.update_animacia()

            # Limit FPS a dt pre update hry
            dt = clock.tick(60) / 1000

        pygame.quit()


