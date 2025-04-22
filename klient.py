import requests

SERVER_URL = "https://9cf54da1-84f4-45d0-b6fd-0817a0a4a654-00-2s3626w9v692a.janeway.replit.dev/"

def send_time_to_server(time_str):
    response = requests.post(
        f"{SERVER_URL}/submit-time",
        json={"time": time_str}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"🕒 Server odpovedal: {data['message']} | Čas: {data['time']}")
    else:
        print("Chyba pri odosielaní času na server.")

# Odoslanie času
send_time_to_server("01:23:45")  # Tento čas bude poslaný na server
