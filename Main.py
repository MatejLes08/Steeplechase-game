from ui import UI, Screen
from Game import Game
from Horse import Horse

ui = None  # Globálna premenna UI

def main():
    global ui
    spusti_hru()

def spusti_hru(restart_to_game=False):
    global ui

    horse = Horse()
    game = Game(
        update_ui_callback=None,
        update_record_callback=None,
        horse=horse,
        meno_hraca=""
    )

    def update_ui(rychlost, ostava, sila, cas_str, pretazenie, map_name):
        # Aktualizuje UI s hernými údajmi vrátane názvu mapy
        ui.rychlost = rychlost
        ui.neprejdenych = ostava
        ui.energia = sila
        ui.stopky = cas_str
        ui.pretazenie = pretazenie
        ui.draw_ui()

    def update_record(cas, timestamp, osobny):
        # Aktualizuje rekordy v UI s celkovým a osobným časom
        ui.update_record(cas, timestamp, osobny)

    game.update_ui = update_ui
    game.update_record = update_record

    def pridaj_rychlost():
        if not game.running_game and game.prejdene_metre < game.DRAHA:
            game.start_race()
            horse.pridaj_rychlost()
            game.kon_rychlost = horse.get_rychlost()
        elif game.running_game:
            horse.pridaj_rychlost()
            game.kon_rychlost = horse.get_rychlost()

    def spomal_rychlost():
        if game.running_game:
            horse.spomal_rychlost()
            game.kon_rychlost = horse.get_rychlost()

    def koniec():
        ui.zatvor()

    # Ak je UI už vytvorené, znovu ho použijeme
    if ui is None:
        ui = UI(
            pridaj_callback=pridaj_rychlost,
            spomal_callback=spomal_rychlost,
            koniec_callback=koniec,
            gamec=game,
            horse=horse
        )
    else:
        ui.horse = horse
        ui.game = game
        ui.pridaj_callback = pridaj_rychlost
        ui.spomal_callback = spomal_rychlost
        ui.koniec_callback = koniec

    # Nastavenie vybranej mapy
    if ui.selected_map_index < len(ui.biomes):
        game.set_map(ui.biomes[ui.selected_map_index]["map_json"])

    ui.set_game(game)
    game.set_ui(ui)
    ui.set_restart_callback(lambda restart: spusti_hru(restart))

    # Resetovanie UI a spustenie na správnej obrazovke
    ui.reset()
    if not restart_to_game:
        ui.current_screen = Screen.MENU
    else:
        ui.current_screen = Screen.GAME
        game.running_game = False

    if not (hasattr(ui, 'game') and ui.game and ui.game.running_game):
        ui.run()

if __name__ == "__main__":
    main()