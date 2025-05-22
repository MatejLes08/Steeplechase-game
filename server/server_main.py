from flask import Flask, request, jsonify
import json
import os

# Inicializácia Flask aplikácie
app = Flask(__name__)
# Názov súboru na ukladanie časov
RECORD_FILE = "casy.json"

def save_time(time, name=""):
    # Uloží čas a meno hráča do JSON súboru
    times = []
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                times = json.load(file)
            except (json.JSONDecodeError, ValueError):
                # Ak súbor nie je platný JSON, inicializuje prázdny zoznam
                times = []
    times.append({"time": time, "name": name})
    with open(RECORD_FILE, "w") as file:
        # Uloží aktualizovaný zoznam časov do súboru
        json.dump(times, file, ensure_ascii=False, indent=2)

def load_times():
    # Načíta zoznam časov zo súboru, vráti prázdny zoznam ak súbor neexistuje
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                return json.load(file)
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

@app.route("/")
def home():
    # Zobrazí HTML stránku so zoradeným zoznamom časov
    all_times = load_times()
    if all_times:
        # Zoradí časy od najrýchlejšieho po najpomalší
        sorted_times = sorted(all_times, key=lambda x: parse_time_to_seconds(x["time"]))
        html = "<h2>Všetky časy (zoradené od najrýchlejšieho):</h2><ol>"
        for entry in sorted_times:
            time = entry["time"]
            name = entry["name"] if entry["name"] else "Anonymný hráč"
            html += f"<li>{name}: {time}</li>"
        html += "</ol>"
        return html
    else:
        return "<p>Zatiaľ nie sú uložené žiadne časy.</p>"

@app.route("/submit-time", methods=["POST"])
def submit_time():
    # Spracuje POST požiadavku na uloženie nového času a mena
    data = request.get_json()
    new_time = data.get("time", "")
    name = data.get("name", "")
    save_time(new_time, name)
    return jsonify({"message": "Čas a meno boli úspešne uložené!", "time": new_time, "name": name}), 200

@app.route("/all-times", methods=["GET"])
def all_times():
    # Vráti zoznam všetkých časov ako JSON
    return jsonify({"times": load_times()}), 200

if __name__ == "__main__":
    # Spustí Flask server na porte 3000
    app.run(host="0.0.0.0", port=3000)