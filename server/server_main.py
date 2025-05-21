from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
RECORD_FILE = "casy.json"

def save_time(time, name=""):
    times = []
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                times = json.load(file)
            except (json.JSONDecodeError, ValueError):
                times = []
    times.append({"time": time, "name": name})
    with open(RECORD_FILE, "w") as file:
        json.dump(times, file, ensure_ascii=False, indent=2)

def load_times():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                return json.load(file)
            except (json.JSONDecodeError, ValueError):
                return []
    return []

def parse_time_to_seconds(time_str):
    try:
        minutes, seconds, hundredths = map(int, time_str.strip().split(":"))
        total_seconds = minutes * 60 + seconds + (hundredths / 100)
        return total_seconds
    except:
        return float('inf')

@app.route("/")
def home():
    all_times = load_times()
    if all_times:
        # Zoradiť podľa času
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
    data = request.get_json()
    new_time = data.get("time", "")
    name = data.get("name", "")
    save_time(new_time, name)
    return jsonify({"message": "Čas a meno boli úspešne uložené!", "time": new_time, "name": name}), 200

@app.route("/all-times", methods=["GET"])
def all_times():
    return jsonify({"times": load_times()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

