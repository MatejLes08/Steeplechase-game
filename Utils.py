class Utils:
    @staticmethod
    def cas_na_stotiny(cas_str):
        """Prevod formátu MM:SS:SS (minúty, sekundy, stotiny) na počet stotín"""
        try:
            minuty, sekundy, stotiny = cas_str.split(":")
            return int(minuty) * 6000 + int(sekundy) * 100 + int(stotiny)
        except ValueError:
            return 0

    @staticmethod
    def stotiny_na_cas(stotiny):
        """Prevod stotín na formát MM:SS:SS (napr. 1:09:84)"""
        minuty = stotiny // 6000
        zvysok = stotiny % 6000
        sekundy = zvysok // 100
        stotiny = zvysok % 100
        return f"{minuty}:{sekundy:02d}:{stotiny:02d}"

    @staticmethod
    def ulozit_cas(cas, nazov_suboru="casy.txt"):
        with open(nazov_suboru, "a") as file:
            file.write(cas + "\n")

    @staticmethod
    def najnizsi_cas(nazov_suboru="casy.txt"):
        try:
            with open(nazov_suboru, "r") as file:
                casy = file.readlines()
        except FileNotFoundError:
            return "N/A"

        casy = [cas.strip() for cas in casy if ":" in cas]
        casy_v_stotinach = [Utils.cas_na_stotiny(cas) for cas in casy]

        if casy_v_stotinach:
            najnizsi = min(casy_v_stotinach)
            return Utils.stotiny_na_cas(najnizsi)
        else:
            return "N/A"
    @staticmethod
    def map_range(value, from_min, from_max, to_min, to_max):
        # Prevod na nový rozsah
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
