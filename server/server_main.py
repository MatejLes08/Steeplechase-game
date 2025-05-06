from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
RECORD_FILE = "casy.json"

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

def load_times():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as file:
            try:
                return json.load(file)
            except (json.JSONDecodeError, ValueError):
                return []
    return []

@app.route("/")
def home():
    all_times = load_times()
    if all_times:
        html = "<h2>Všetky časy:</h2><ol>"
        for t in all_times:
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
    return jsonify({"message": "Čas bol úspešne uložený!", "time": new_time}), 200

@app.route("/all-times", methods=["GET"])
def all_times():
    return jsonify({"times": load_times()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
