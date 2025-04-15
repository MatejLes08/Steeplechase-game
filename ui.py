import pygame
from Utils import Utils

class UI:
    def __init__(self, pridaj_callback, spomal_callback, start_callback, koniec_callback):
        pygame.init()

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

    def draw_ui(self):
        self.screen.fill(self.ORANGE)

        def draw_text(label, value, x, y):
            text = self.font.render(f"{label}: {value}", True, self.BLACK)
            self.screen.blit(text, (x, y))

        draw_text("Rýchlosť", self.rychlost, 8, 70)
        draw_text("Energia", self.energia, 92, 21)
        draw_text("Do cieľa", self.neprejdenych, 279, 15)
        draw_text("Terén", self.aktualna_draha, 8, 113)
        draw_text("Čas", self.stopky, 565, 15)
        draw_text("Rekord", self.rekord, 580, 70)

        pygame.draw.rect(self.screen, self.GRAY, self.button_cancel)
        pygame.draw.rect(self.screen, self.GRAY, self.button_decrease)
        pygame.draw.rect(self.screen, self.GRAY, self.button_increase)
        pygame.draw.rect(self.screen, self.GRAY, self.button_start)

        def render_button_text(text, rect):
            label = self.font.render(text, True, self.BLACK)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

        render_button_text("zrušiť", self.button_cancel)
        render_button_text("spomaľ", self.button_decrease)
        render_button_text("pridaj", self.button_increase)
        render_button_text("štart", self.button_start)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_cancel.collidepoint(event.pos):
                    self.koniec_callback()
                elif self.button_decrease.collidepoint(event.pos):
                    self.spomal_callback()
                elif self.button_increase.collidepoint(event.pos):
                    self.pridaj_callback()
                elif self.button_start.collidepoint(event.pos):
                    self.start_callback()
        return True

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw_ui()
        pygame.quit()
