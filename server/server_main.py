from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

RECORD_FILE = "casy.json"


# Funkcia na ukladanie času do JSON súboru
def save_time(time):
    times = []

    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                times = json.load(file)
            except (json.JSONDecodeError, ValueError):
                times = []

    times.append(time)

    with open(RECORD_FILE, "w") as file:
        json.dump(times, file, ensure_ascii=False, indent=2)


# Funkcia na získanie troch najlepších časov
# Predpokladá, že časy sú vo formáte "HH:MM:SS"
def get_top_times():
    times = []
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                times = json.load(file)
            except (json.JSONDecodeError, ValueError):
                return []

    # Konverzia na sekundy pre porovnanie
    def to_seconds(t):
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s

    times_sorted = sorted(times, key=to_seconds)
    return times_sorted[:3]


@app.route("/")
def home():
    top_times = get_top_times()
    if top_times:
        html = "<h2>Top 3 časy:</h2><ol>"
        for t in top_times:
            html += f"<li>{t}</li>"
        html += "</ol>"
        return html
    else:
        return "<p>Zatiaľ nie sú uložené žiadne časy.</p>"


@app.route("/submit-time", methods=["POST"])
def submit_time():
    data = request.get_json()
    new_time = data.get("time", "")

    save_time(new_time)

    return jsonify({
        "message": "Čas bol úspešne uložený!",
        "time": new_time
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)