import tkinter

class UI:
    def __init__(self, pridaj_callback, spomal_callback, start_callback, koniec_callback):
        self.okno = tkinter.Tk()
        self.okno.title("Steeplchase preteky")
        self.okno.configure(bg="#FFC66F")

        self.rychlost = tkinter.IntVar()
        self.energia = tkinter.IntVar()
        self.neprejdenych = tkinter.IntVar()
        self.aktualna_draha = tkinter.StringVar()
        self.stopky = tkinter.StringVar()
        self.rekord = tkinter.StringVar(value=najnizsi_cas())

        # Štítky a políčka
        tkinter.Label(self.okno, text="Aktulna rýchlosť:", bg="#FFC66F", width=20).grid(row=0, column=0)
        tkinter.Entry(self.okno, textvariable=self.rychlost, bg="#dc7800", fg="white", width=10).grid(row=0, column=1)

        tkinter.Label(self.okno, text="Energia koňa:", bg="#FFC66F", width=20).grid(row=1, column=0)
        tkinter.Entry(self.okno, textvariable=self.energia, bg="#dc7800", fg="white", width=10).grid(row=1, column=1)

        tkinter.Label(self.okno, text="Počet metrov do cieľa:", bg="#FFC66F", width=20).grid(row=2, column=0)
        tkinter.Entry(self.okno, textvariable=self.neprejdenych, bg="#dc7800", fg="white", width=10).grid(row=2, column=1)

        tkinter.Label(self.okno, text="Terén", bg="green", width=15).grid(row=0, column=2)
        tkinter.Entry(self.okno, textvariable=self.aktualna_draha, bg="#dc7800", fg="white", width=15).grid(row=1, column=2)

        tkinter.Label(self.okno, text="Čas:", bg="#FFC66F", width=20).grid(row=3, column=0)
        tkinter.Entry(self.okno, textvariable=self.stopky, bg="#dc7800", fg="white", width=10).grid(row=3, column=1)

        tkinter.Label(self.okno, text="Rekord:", bg="#b50000", width=15).grid(row=2, column=2)
        tkinter.Entry(self.okno, textvariable=self.rekord, bg="#dc7800", fg="white", width=5).grid(row=3, column=2)

        # Tlačidlá s prepojením na callbacky
        tkinter.Button(self.okno, width=10, text="zrušiť", bg="red", command=koniec_callback).grid(row=3, column=3)
        tkinter.Button(self.okno, width=10, text="Pridaj", bg="#b9b9b9", command=pridaj_callback).grid(row=1, column=3)
        tkinter.Button(self.okno, width=10, text="Spomaľ", bg="#b9b9b9", command=spomal_callback).grid(row=2, column=3)
        tkinter.Button(self.okno, width=10, text="Štart", bg="#9cff71", command=start_callback).grid(row=0, column=3)

    def aktualizuj(self):
        self.okno.update()

    def spustit(self):
        self.okno.mainloop()

    def zatvor(self):
        self.okno.destroy()
