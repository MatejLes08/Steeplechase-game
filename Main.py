from ui import UI
from Game import Game
from Horse import Horse
from terrain import Terrain
from ui import Utils


def main():
    horse = Horse()

    # Vytvorenie objektu Game
    game = Game(update_ui_callback=None, update_record_callback=None)  # Dočasne None

    # Funkcia na aktualizovanie UI počas pretekov
    def update_ui(rychlost, ostava, sila, cas_str):
        ui.rychlost = rychlost
        ui.neprejdenych = ostava
        ui.energia = sila
        ui.stopky = cas_str

        # Použi terrain z game
        oddych_cis, zrychlenie, narocnost, bonus, typ_terenu = game.terrain.zisti_pasmo(ostava)
        ui.aktualna_draha = typ_terenu
        ui.draw_ui()

    # Funkcia na aktualizáciu rekordu po dojazde
    def update_record(record):
        ui.rekord = record

    # Teraz nastavíme späť správne callbacky
    game.update_ui = update_ui
    game.update_record = update_record

    # Callback funkcie pre UI
    def pridaj_rychlost():
        horse.pridaj_rychlost()
        game.kon_rychlost = horse.get_rychlost()

    def spomal_rychlost():
        horse.spomal_rychlost()
        game.kon_rychlost = horse.get_rychlost()

    def start():
        game.kon_max_rychlost = horse.max_rychlost
        game.kon_vydrz = horse.vydrz

        game.start_race()

    def koniec():
        ui.zatvor()

    # Vytvorenie UI
    ui = UI(pridaj_callback=pridaj_rychlost,
            spomal_callback=spomal_rychlost,
            start_callback=start,
            koniec_callback=koniec)

    # Spustenie GUI
    ui.set_game(game)
    ui.run()




if __name__ == "__main__":
    main()
