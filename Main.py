from ui import UI
from Game import Game
from Horse import Horse
from ui import Utils


def main():
    horse = Horse()

    # Vytvorenie objektu Game
    game = Game(update_ui_callback=None, update_record_callback=None, horse = horse)  # Dočasne None

    # Funkcia na aktualizovanie UI počas pretekov
    def update_ui(rychlost, ostava, sila, cas_str, pretazenie):
        ui.rychlost = rychlost
        ui.neprejdenych = ostava
        ui.energia = sila
        ui.stopky = cas_str
        ui.pretazenie = pretazenie
        
        ui.draw_ui(horse)

    # Funkcia na aktualizáciu rekordu po dojazde
    def update_record(record):
        ui.rekord = record

    # nastavenie callbackov
    game.update_ui = update_ui
    game.update_record = update_record

    # Callback funkcie pre UI
    def pridaj_rychlost():
        if game.running_game == False and game.prejdene_metre < game.DRAHA:
            game.start_race()
        else:
            horse.pridaj_rychlost()
            game.kon_rychlost = horse.get_rychlost()

    def spomal_rychlost():
        horse.spomal_rychlost()
        game.kon_rychlost = horse.get_rychlost()

        

    def koniec():
        ui.zatvor()

    # Vytvorenie UI
    ui = UI(pridaj_callback=pridaj_rychlost,
            spomal_callback=spomal_rychlost,
            koniec_callback=koniec, gamec=game)

    # Spustenie GUI
    ui.set_game(game)
    ui.run(horse)




if __name__ == "__main__":
    main()
