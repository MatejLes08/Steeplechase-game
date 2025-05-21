import requests

class Utils:
    SERVER_URLh = "https://9cf54da1-84f4-45d0-b6fd-0817a0a4a654-00-2s3626w9v692a.janeway.replit.dev"
    SERVER_URL = "https://2fc243c1-0d24-4361-8a3a-90e456b711aa-00-ddze6lg31kxv.picard.replit.dev/"

    @staticmethod
    def cas_na_stotiny(cas_str):
        parts = cas_str.split(":")
        if len(parts) == 3:
            minuty, sekundy, stotiny = parts
        elif len(parts) == 2:
            minuty, sekundy = parts
            stotiny = "0"
        else:
            return 0
        try:
            return int(minuty) * 6000 + int(sekundy) * 100 + int(stotiny)
        except ValueError:
            return 0

    @staticmethod
    def stotiny_na_cas(stotiny):
        minuty = stotiny // 6000
        zvysok = stotiny % 6000
        sekundy = zvysok // 100
        stotiny = zvysok % 100
        return f"{minuty}:{sekundy:02d}:{stotiny:02d}"

    @staticmethod
    def ulozit_cas(cas, meno=""):
        # Odoslanie času a mena na server
        try:
            response = requests.post(
                f"{Utils.SERVER_URL}/submit-time",
                json={"time": cas, "name": meno}
            )
            if response.status_code == 200:
                print(f"[✓] Čas a meno boli odoslané na server: {meno} - {cas}")
        except requests.RequestException as e:
            print(f"[X] Chyba pri odosielaní času a mena na server: {e}")

    @staticmethod
    def extrahuj_cas_na_stotiny(zaznam):
        return Utils.cas_na_stotiny(zaznam["time"])

    @staticmethod
    def najnizsi_cas():
        try:
            response = requests.get(f"{Utils.SERVER_URL}/all-times")
            if response.status_code == 200:
                times = response.json().get("times", [])
                if not times:
                    return "N/A"
                najnizsi = min(times, key=Utils.extrahuj_cas_na_stotiny)
                return najnizsi["time"]  # Vraciam iba čas ako reťazec
        except requests.RequestException:
            pass
        return "N/A"

    @staticmethod
    def map_range(value, from_min, from_max, to_min, to_max):
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min