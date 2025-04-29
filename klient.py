import requests

class Klient:
    def __init__(self, server_url):
        self.server_url = server_url

    def odosli_cas(self, cas_str):
        try:
            response = requests.post(
                f"{self.server_url}/submit-time",
                json={"time": cas_str}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"🕒 Server odpovedal: {data['message']} | Čas: {data['time']}")
            else:
                print("Chyba pri odosielaní času na server.")
        except requests.RequestException as e:
            print(f"Vyskytla sa výnimka pri pripojení k serveru: {e}")

SERVER_URL = "https://9cf54da1-84f4-45d0-b6fd-0817a0a4a654-00-2s3626w9v692a.janeway.replit.dev/"
klient = Klient(SERVER_URL)
klient.odosli_cas("01:23:45")