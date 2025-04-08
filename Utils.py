class Utils:
    @staticmethod
    def cas_na_sekundy(cas_str):
        minuty, sekundy = cas_str.split(":")
        sekundy_celkom = int(minuty) * 60 + int(sekundy)
        return sekundy_celkom

    @staticmethod
    def sekundy_na_cas(sekundy):
        minuty = sekundy // 60
        sekundy = sekundy % 60
        cas_str = f"{minuty}:{sekundy:02d}"
        return cas_str

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
        casy_v_sekundach = [Utils.cas_na_sekundy(cas) for cas in casy]

        if casy_v_sekundach:
            najnizsi_cas_v_sekundach = min(casy_v_sekundach)
            return Utils.sekundy_na_cas(najnizsi_cas_v_sekundach)
        else:
            return "N/A"
