from ui import UI
from Game import Game
from Horse import Horse
from ui import Utils


ui = None  # Globálna premenna UI

def main():
    spusti_hru()


def spusti_hru():
    global ui

    horse = Horse()

    game = Game(update_ui_callback=None,
                update_record_callback=None,
                horse=horse,
                meno_hraca="Meno")

    def update_ui(rychlost, ostava, sila, cas_str, pretazenie):
        ui.rychlost = rychlost
        ui.neprejdenych = ostava
        ui.energia = sila
        ui.stopky = cas_str
        ui.pretazenie = pretazenie
        ui.draw_ui()

    def update_record(cas, timestamp):
        ui.rekord = cas

    game.update_ui = update_ui
    game.update_record = update_record

    def pridaj_rychlost():
        if not game.running_game and game.prejdene_metre < game.DRAHA:
            game.start_race()
        else:
            horse.pridaj_rychlost()
            game.kon_rychlost = horse.get_rychlost()

    def spomal_rychlost():
        horse.spomal_rychlost()
        game.kon_rychlost = horse.get_rychlost()

    def koniec():
        ui.zatvor()

    # Ak je UI už vytvorené, znovu ho použijeme
    if ui is None:
        ui = UI(pridaj_callback=pridaj_rychlost,
                spomal_callback=spomal_rychlost,
                koniec_callback=koniec,
                gamec=game,
                horse=horse)
        ui.set_game(game)
        ui.set_restart_callback(spusti_hru)
        ui.run()
    else:
        ui.reset(
            horse=horse,
            game=game,
            pridaj=pridaj_rychlost,
            spomal=spomal_rychlost,
            koniec=koniec,
            update_ui=update_ui,
            update_record=update_record
        )


if __name__ == "__main__":
    main()