from ui import UI
from Game import Game
from Horse import Horse
from terrain import Terrain
from ui import Utils


def main():
    horse = Horse()
    terrain = Terrain()

    # Funkcia na aktualizovanie UI počas pretekov
    def update_ui(rychlost, ostava, sila, cas_str):
        ui.rychlost.set(rychlost)
        ui.neprejdenych.set(ostava)
        ui.energia.set(sila)
        ui.stopky.set(cas_str)

        oddych_cis, zrychlenie, narocnost, bonus, typ_terenu = terrain.zisti_pasmo(ostava)
        ui.aktualna_draha.set(typ_terenu)
        ui.aktualizuj()

    # Funkcia na aktualizáciu rekordu po dojazde
    def update_record(record):
        ui.rekord.set(record)

    # Vytvorenie objektu Game
    game = Game(update_ui_callback=update_ui, update_record_callback=update_record)

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

        # Preteky prebiehajú v hlavnej slučke, jednoduchý beh bez vlákien
        game.start_race()

    def koniec():
        ui.zatvor()

    # Vytvorenie UI
    ui = UI(pridaj_callback=pridaj_rychlost,
            spomal_callback=spomal_rychlost,
            start_callback=start,
            koniec_callback=koniec)

    # Spustenie GUI
    ui.spustit()


if __name__ == "__main__":
    main()
