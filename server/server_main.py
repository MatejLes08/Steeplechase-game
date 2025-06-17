from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timedelta

# Inicializácia Flask aplikácie
app = Flask(__name__)
# Názov súboru na ukladanie časov
RECORD_FILE = "casy.json"

def save_time(time, name="", map_name="mapa1"):
    # Uloží čas, meno hráča, názov mapy a časovú pečiatku do JSON súboru
    times = []
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                times = json.load(file)
            except (json.JSONDecodeError, ValueError):
                # Ak súbor nie je platný JSON, inicializuje prázdny zoznam
                times = []
    # Vytvorenie časovej pečiatky vo formáte DD.MM.YYYY HH:MM:SS s korekciou +2 hodiny
    timestamp = (datetime.now() + timedelta(hours=2)).strftime("%d.%m.%Y %H:%M:%S")
    times.append({"time": time, "name": name, "map": map_name, "timestamp": timestamp})
    with open(RECORD_FILE, "w") as file:
        # Uloží aktualizovaný zoznam časov do súboru
        json.dump(times, file, ensure_ascii=False, indent=2)

def load_times(map_name=None):
    # Načíta zoznam časov zo súboru, filtrovaný podľa mapy ak je zadaná, vráti prázdny zoznam ak súbor neexistuje
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                all_times = json.load(file)
                # Ak je zadaná mapa, filtrujeme podľa nej
                if map_name:
                    all_times = [entry for entry in all_times if entry.get("map") == map_name]
                # Filtrovať na najlepší čas pre každého hráča
                best_times = {}
                for entry in all_times:
                    name = entry["name"] if entry["name"] else "Anonymný hráč"
                    time_stotiny = parse_time_to_seconds(entry["time"])
                    if name not in best_times or time_stotiny < parse_time_to_seconds(best_times[name]["time"]):
                        best_times[name] = entry
                return list(best_times.values())
            except (json.JSONDecodeError, ValueError):
                return []
    return []

def parse_time_to_seconds(time_str):
    # Prevedie čas vo formáte "minúty:sekundy:stotiny" na sekundy pre porovnanie
    try:
        minutes, seconds, hundredths = map(int, time_str.strip().split(":"))
        total_seconds = minutes * 60 + seconds + (hundredths / 100)
        return total_seconds
    except:
        # Vráti nekonečno pri chybe parsovania pre účely triedenia
        return float('inf')

def sort_key(entry):
    # Kľúčová funkcia pre triedenie časov podľa času prevedeného na sekundy
    return parse_time_to_seconds(entry["time"])

@app.route("/")
def home():
    # Zobrazí HTML stránku so zoradeným zoznamom časov pre každú mapu
    maps = ["mapa1", "mapa2", "mapa3"]  # Zoznam dostupných máp
    html = """
    <style>
        li { margin-bottom: 15px; }
        h3 { margin-top: 20px; }
    </style>
    <h2>Všetky časy (zoradené od najrýchlejšieho):</h2>
    """
    for map_name in maps:
        all_times = load_times(map_name)
        if all_times:
            # Zoradí časy od najrýchlejšieho po najpomalší pomocou sort_key
            sorted_times = sorted(all_times, key=sort_key)
            html += f"<h3>Mapa: {map_name}</h3><ol>"
            for entry in sorted_times:
                time = entry["time"]
                name = entry["name"] if entry["name"] else "Anonymný hráč"
                timestamp = entry.get("timestamp", "Není známo")
                html += f"<li>{time} - {name} ({timestamp})</li>"
            html += "</ol>"
        else:
            html += f"<h3>Mapa: {map_name}</h3><p>Zatiaľ nie sú uložené žiadne časy.</p>"
    return html

@app.route("/submit-time", methods=["POST"])
def submit_time():
    # Spracuje POST požiadavku na uloženie nového času, mena a mapy
    data = request.get_json()
    new_time = data.get("time", "")
    name = data.get("name", "")
    map_name = data.get("map", "mapa1")  # Predvolená mapa, ak nie je zadaná
    save_time(new_time, name, map_name)
    return jsonify({"message": "Čas a meno boli úspešne uložené!", "time": new_time, "name": name, "map": map_name}), 200

@app.route("/all-times", methods=["GET"])
def all_times():
    # Vráti zoznam všetkých časov ako JSON, filtrovaný podľa mapy ak je zadaná
    map_name = request.args.get("map")  # Získa parameter mapy z URL
    return jsonify({"times": load_times(map_name)}), 200

if __name__ == "__main__":
    # Spustí Flask server na porte 3000
    app.run(host="0.0.0.0", port=3000)