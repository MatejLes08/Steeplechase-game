import tkinter
import time
import random


def cas_na_sekundy(cas_str):
    minuty, sekundy = cas_str.split(":")
    sekundy_celkom = int(minuty) * 60 + int(sekundy)
    return sekundy_celkom


def sekundy_na_cas(sekundy):
    minuty = sekundy // 60
    sekundy = sekundy % 60
    cas_str = f"{minuty}:{sekundy:02d}"
    return cas_str


def ulozit_cas(cas):
    with open("casy.txt", "a") as file:
        file.write(cas + "\n")


def najnizsi_cas():
    with open("casy.txt", "r") as file:
        casy = file.readlines()

    casy = [cas.strip() for cas in casy]
    casy_v_sekundach = []

    for cas in casy:
        if ":" in cas:
            sekundy = cas_na_sekundy(cas)
            casy_v_sekundach.append(sekundy)

    if casy_v_sekundach:
        najnizsi_cas_v_sekundach = min(casy_v_sekundach)
        najnizsi_cas = sekundy_na_cas(najnizsi_cas_v_sekundach)
    else:
        najnizsi_cas = "N/A"

    return najnizsi_cas


def pridaj():
    global kon_rychlost
    if sila != 0:
        if kon_rychlost != kon_max_rychlost:
            kon_rychlost += 4
    rychlost.set(kon_rychlost)
    okno.update()


def spomal():
    global kon_rychlost
    if kon_rychlost != 0:
        kon_rychlost -= 4
    rychlost.set(kon_rychlost)
    okno.update()


def generacia_terenu():
    udalost = [random.randint(400, 1000), random.randint(1400, 1800)]
    random.shuffle(udalost)

    miesto_narocneho_pasma = udalost[0]
    miesto_sprinterskeho_pasma = udalost[1]

    napajadlo1 = random.randint(1600, 2000)
    napajadlo2 = random.randint(800, 1580)
    napajadlo3 = random.randint(20, 780)

    return miesto_narocneho_pasma, miesto_sprinterskeho_pasma, napajadlo1, napajadlo2, napajadlo3


def zisti_pasmo(ostava, mnp, msp, n1, n2, n3):
    oddych_cis = 0.01
    zrychlenie = 1
    narocnost = 7000
    bonus = 1

    if mnp >= ostava >= mnp - 300:
        aktualna_draha.set("Náročné pásmo")
        narocnost = 5000
        zrychlenie = 1
        oddych_cis = 0.005

    elif msp >= ostava >= msp - 400:
        aktualna_draha.set("Šprintérske pásmo")
        oddych_cis = 0.01
        zrychlenie = 1.25

    if n1 >= ostava >= n1 - 20 or n2 >= ostava >= n2 - 20 or n3 >= ostava >= n3 - 20:
        aktualna_draha.set("Napájadlo")
        bonus = 10

    return oddych_cis, zrychlenie, narocnost, bonus


def tik():
    global prejdene_metre, zataz, kon_rychlost, sila, draha, cas, minuty
    mnp, msp, n1, n2, n3 = generacia_terenu()
    print(mnp, msp, n1, n2, n3)
    ostava = 2000

    while not draha <= prejdene_metre:
        time.sleep(0.01)
        aktualna_draha.set("cesta")
        cas += 0.01
        if int(cas) >= 60:
            cas = cas - 60
            minuty += 1
        stopky.set(str(f"{minuty}:{int(cas)}"))

        oddych_cis, zrychlenie, narocnost, bonus = zisti_pasmo(ostava, mnp, msp, n1, n2, n3)

        # Normálny terén

        if kon_rychlost == 0:
            if sila < 100:
                zataz -= oddych_cis * 2 * bonus

        elif sila <= 0:
            kon_rychlost = 4
            rychlost.set(int(kon_rychlost))

        elif kon_rychlost <= 12:
            if sila < 100:
                zataz -= oddych_cis

        elif kon_rychlost <= 24:
            zataz += kon_rychlost / narocnost

        elif kon_rychlost > 24 and kon_rychlost < 50:
            zataz += kon_rychlost / (narocnost - 2000)

        else:
            zataz += kon_rychlost / (narocnost - 3000)

        sila = kon_vydrz - zataz
        print(zataz)

        prejdene_metre += kon_rychlost*zrychlenie / 3.6 * 0.01
        ostava = round(draha - prejdene_metre)

        neprejdenych.set(ostava)
        rychlost.set(int(kon_rychlost * zrychlenie))
        energia.set(int(sila))
        okno.update()

    cas_str = f"{minuty}:{int(cas):02d}"
    ulozit_cas(cas_str)
    najnizsi = najnizsi_cas()
    rekord.set(str(najnizsi))


def koniec():
    okno.destroy()


prejdene_metre = 0
draha = 2000
kon_rychlost = 0
kon_max_rychlost = 60
kon_vydrz = 100
zataz = 0
sila = 100

cas = 0
minuty = 0

okno = tkinter.Tk()
okno.title("Steeplchase preteky")
svetlotelova = "#FFC66F"
hneda = "#dc7800"
svetl_hneda = "#b86400"
siva = "#B7B7B7"
cervena = "#b50000"
zelena = "#9cff71"
okno.configure(bg=svetlotelova)

tkinter.Label(okno, text="Aktulna rýchlosť:", bg=svetlotelova, width=20).grid(row=0, column=0)
rychlost = tkinter.IntVar()
tkinter.Entry(okno, textvariable=rychlost, bg=hneda, fg="white", width=10).grid(row=0, column=1)

tkinter.Label(okno, text="Počet metrov do cieľa:", bg=svetlotelova, width=20).grid(row=2, column=0)
neprejdenych = tkinter.IntVar()
tkinter.Entry(okno, textvariable=neprejdenych, bg=hneda, fg="white", width=10).grid(row=2, column=1)

tkinter.Label(okno, text="Energia koňa:", bg=svetlotelova, width=20).grid(row=1, column=0)
energia = tkinter.IntVar()
tkinter.Entry(okno, textvariable=energia, bg=hneda, fg="white", width=10).grid(row=1, column=1)

tkinter.Label(okno, text="Terén", bg="green", width=15).grid(row=0, column=2)
aktualna_draha = tkinter.StringVar()
tkinter.Entry(okno, textvariable=aktualna_draha, bg=hneda, fg="white", width=15).grid(row=1, column=2)

tkinter.Label(okno, text="Čas:", bg=svetlotelova, width=20).grid(row=3, column=0)
stopky = tkinter.StringVar()
tkinter.Entry(okno, textvariable=stopky, bg=hneda, fg="white", width=10).grid(row=3, column=1)

tkinter.Label(okno, text="Rekord:", bg=cervena, width=15).grid(row=2, column=2)
rekord = tkinter.StringVar(value=najnizsi_cas())
tkinter.Entry(okno, textvariable=rekord, bg=hneda, fg="white", width=5).grid(row=3, column=2)

tkinter.Button(okno, width=10, text="zrušiť", bg="red", command=koniec).grid(row=3, column=3)
tkinter.Button(okno, width=10, text="Pridaj", bg="#b9b9b9", command=pridaj).grid(row=1, column=3)
tkinter.Button(okno, width=10, text="Spomaľ", bg="#b9b9b9", command=spomal).grid(row=2, column=3)
tkinter.Button(okno, width=10, text="Štart", bg=zelena, command=tik).grid(row=0, column=3)

okno.mainloop()
