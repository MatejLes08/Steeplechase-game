import pygame
from Utils import Utils
from Horse import Horse

class UI:
    def __init__(self, pridaj_callback, spomal_callback, start_callback, koniec_callback,gamec):
        pygame.init()

        
        self.game = gamec

        self.width = 800
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Steeplchase preteky")
        self.font = pygame.font.SysFont(None, 40)
        self.fontMetre = pygame.font.SysFont(None, 110)
        self.fontCas = pygame.font.SysFont("Arial", 70)

        # farby
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.DARKGRAY = (100, 100, 100)
        self.BLACK = (0, 0, 0)
        self.ORANGE = (255, 198, 111)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)

        # premenné
        self.rychlost = 0
        self.energia = 100
        self.neprejdenych = 0
        self.aktualna_draha = ""
        self.stopky = "0:00:00"
        self.rekord = Utils.najnizsi_cas()
        self.pretazenie = 0

        # tlačidlá
        self.button_cancel = pygame.Rect(32, 433, 150, 50)
        self.button_decrease = pygame.Rect(216, 433, 150, 50)
        self.button_increase = pygame.Rect(416, 433, 150, 50)
        self.button_start = pygame.Rect(632, 433, 150, 50)

        # callback funkcie
        self.pridaj_callback = pridaj_callback
        self.spomal_callback = spomal_callback
        self.start_callback = start_callback
        self.koniec_callback = koniec_callback

        # Získanie terénu z Game
        self.draha = self.game.get_terrain_path()


    

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
        pygame.draw.rect(self.screen, self.GREEN, self.button_start)

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
            if self.game:
                self.game.update(dt)

            self.draw_ui(horse)
            horse.update_animacia()

            dt = clock.tick(60) / 1000  # dt v sekundách

        pygame.quit()

