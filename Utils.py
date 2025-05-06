import requests

class Utils:
    SERVER_URL = "https://9cf54da1-84f4-45d0-b6fd-0817a0a4a654-00-2s3626w9v692a.janeway.replit.dev"

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
    def ulozit_cas(cas):
        # Odoslanie času na server
        try:
            response = requests.post(
                f"{Utils.SERVER_URL}/submit-time",
                json={"time": cas}
            )
            if response.status_code == 200:
                print(f"[✓] Čas bol odoslaný na server: {cas}")
        except requests.RequestException as e:
            print(f"[X] Chyba pri odosielaní času na server: {e}")

    @staticmethod
    def najnizsi_cas():
        try:
            response = requests.get(f"{Utils.SERVER_URL}/all-times")
            if response.status_code == 200:
                times = response.json().get("times", [])
                if not times:
                    return "N/A"
                najnizsi = min(times, key=Utils.cas_na_stotiny)
                return najnizsi
        except requests.RequestException:
            pass
        return "N/A"

    @staticmethod
    def map_range(value, from_min, from_max, to_min, to_max):
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min