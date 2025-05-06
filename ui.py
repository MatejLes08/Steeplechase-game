import pygame
from enum import Enum
from Utils import Utils
from Horse import Horse

class Screen(Enum):
    MENU = 1
    GAME = 2

class UI:
    def __init__(self, pridaj_callback, spomal_callback, start_callback, koniec_callback, gamec):
        pygame.init()

        
        self.game = gamec

        self.width = 800
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Steeplchase preteky")
        self.font = pygame.font.SysFont(None, 40)

        # farby
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.DARKGRAY = (100, 100, 100)
        self.BLACK = (0, 0, 0)
        self.ORANGE = (255, 198, 111)

        # premenné
        self.rychlost = 0
        self.energia = 0
        self.neprejdenych = 0
        self.aktualna_draha = ""
        self.stopky = ""
        self.rekord = Utils.najnizsi_cas()
        self.pretazenie = 0

        # Tlačidlá - HRA
        self.button_cancel = pygame.Rect(32, 433, 150, 50)
        self.button_decrease = pygame.Rect(216, 433, 150, 50)
        self.button_increase = pygame.Rect(416, 433, 150, 50)
        self.button_start = pygame.Rect(632, 433, 150, 50)

        # Tlačidlá - MENU
        self.button_start_menu = pygame.Rect(300, 300, 200, 60)

        # callback funkcie
        self.pridaj_callback = pridaj_callback
        self.spomal_callback = spomal_callback
        self.start_callback = start_callback
        self.koniec_callback = koniec_callback

        # Získanie terénu z Game
        self.draha = self.game.get_terrain_path()

        # Riadenie aktuálnej obrazovky
        self.current_screen = Screen.MENU

    def draw_menu(self):
        self.screen.fill(self.ORANGE)
        title = self.font.render("Steeplechase preteky", True, self.BLACK)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        pygame.draw.rect(self.screen, self.GRAY, self.button_start_menu)
        label = self.font.render("Štart hry", True, self.BLACK)
        label_rect = label.get_rect(center=self.button_start_menu.center)
        self.screen.blit(label, label_rect)

        pygame.display.flip()
    

    def draw_ui(self, horse):
        self.screen.fill(self.ORANGE)

        


        # Funkcia na vykreslenie štítku + hodnoty
        def draw_text(label, value, x, y):
            text = self.font.render(f"{label}: {value}", True, self.BLACK)
            self.screen.blit(text, (x, y))

        # Zobrazenie herných údajov
        draw_text("Rýchlosť", self.rychlost, 20, 20)
        draw_text("Energia", self.energia, 20, 60)
        draw_text("Do cieľa", self.neprejdenych, 20, 100)
        if self.game:
            self.aktualna_draha = self.game.get_akt_draha()
        draw_text("Terén", self.aktualna_draha, 20, 140)
        draw_text("Čas", self.stopky, 600, 20)
        draw_text("Rekord", self.rekord, 600, 60)
        draw_text("Preťaženie", self.pretazenie, 600, 100)
      
             # Posúvajúce sa pásy (cesta)
        if self.game:
            posun = self.game.posun_cesty
            sirka = self.game.sirka_useku
            draha = self.draha
            self.offset = -int(posun % sirka)
            start_index = int(posun // sirka)-9

            for i in range(9):
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
        pygame.draw.rect(self.screen, self.GRAY, self.button_cancel)
        pygame.draw.rect(self.screen, self.GRAY, self.button_decrease)
        pygame.draw.rect(self.screen, self.GRAY, self.button_increase)
        pygame.draw.rect(self.screen, self.GRAY, self.button_start)

        # Texty na tlačidlách
        def render_button_text(text, rect):
            label = self.font.render(text, True, self.BLACK)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

        render_button_text("Zrušiť", self.button_cancel)
        render_button_text("Spomaľ", self.button_decrease)
        render_button_text("Pridaj", self.button_increase)
        render_button_text("Štart", self.button_start)

        #vykreslenie obrazku hráča
        self.screen.blit(horse.current_image, (horse.position_x, horse.position_y))

        # Aktualizácia obrazovky
        pygame.display.flip()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.current_screen == Screen.MENU:
                    if self.button_start_menu.collidepoint(event.pos):
                        self.current_screen = Screen.GAME
                elif self.current_screen == Screen.GAME:
                    if self.button_cancel.collidepoint(event.pos):
                        return False
                    elif self.button_decrease.collidepoint(event.pos):
                        self.spomal_callback()
                    elif self.button_increase.collidepoint(event.pos):
                        self.pridaj_callback()
                    elif self.button_start.collidepoint(event.pos):
                        self.start_callback()
        return True

    def set_game(self, game):
        self.game = game

    def run(self, horse):
        clock = pygame.time.Clock()
        dt = 0.0 # dt nastavujem najprv na 0.0, ale potom ho zmením - len, aby to nespadlo na chybe referenced before assignment
        self.game.running = True

        while self.game.running:
            self.game.running = self.handle_events()
            if self.current_screen == Screen.MENU:
                self.draw_menu()
            elif self.current_screen == Screen.GAME:
                if self.game:
                    self.game.update(dt)

                self.draw_ui(horse)
                horse.update_animacia()

            dt = clock.tick(60) / 1000  # dt v sekundách

        pygame.quit()
