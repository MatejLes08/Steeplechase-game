import pygame

class AudioManager:
    def __init__(self):
        pygame.mixer.init()  # Inicializácia mixéra pre zvuk
        self.music_playing = False
        pygame.mixer.music.load("assets/background_music.mp3")  # Cesta k hudbe
        pygame.mixer.music.set_volume(0.03)  # Nastavenie tichej hlasitosti

    def start_music(self):
        # Spustí hudbu, ak ešte nehrá
        if not self.music_playing:
            pygame.mixer.music.play(-1)  # -1 znamená opakované prehrávanie
            self.music_playing = True

    def stop_music(self):
        # Zastaví hudbu a resetuje prehrávanie
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    def pause_music(self):
        # Pozastaví hudbu
        if self.music_playing:
            pygame.mixer.music.pause()

    def unpause_music(self):
        # Obnoví hudbu po pozastavení
        if self.music_playing:
            pygame.mixer.music.unpause()

    def cleanup(self):
        # Uvoľní zdroje pri ukončení
        pygame.mixer.quit()