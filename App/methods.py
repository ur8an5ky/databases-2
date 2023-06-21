from App import app, cursor
import re

def ustaw_koszyk_default():
    for i in range(len(app.config['koszyk'])):
        app.config['koszyk'][i] = (False, 0)

def selects():
    s = app.config['logged_in_id']
    cursor.execute(f'Select Id, CAST(Dane as NVARCHAR(MAX)), CAST(Konto as NVARCHAR(MAX)) FROM Konta WHERE Id = {s}')
    dane = cursor.fetchall()
    cursor.execute(f"Select Id, CAST(Dane as NVARCHAR(MAX)), CAST(Adres as NVARCHAR(MAX)) FROM Uzytkownicy WHERE CAST(Dane as NVARCHAR(MAX)) = '{dane[0][1]}'")
    adres = cursor.fetchall()
    cursor.execute(f"Select CAST(Karta as NVARCHAR(MAX)), CAST(Konto as NVARCHAR(MAX)) FROM Karty WHERE CAST(Konto as NVARCHAR(MAX)) = '{dane[0][2]}'")
    karta = cursor.fetchall()
    if karta:
        karta = [list(krotka) for krotka in karta]
        karta = karta[0][0].replace(" 00:00:00", "").split(';')
        karta = [karta[2][-4:], karta[3].replace(".", "/")[-7:]]
    return dane, adres, karta

def sprawdz_format_stringa(string):
    wzor = r'^(0[1-9]|1[0-2])/20(23|24|25|26|27)$'
    dopasowanie = re.match(wzor, string)
    return dopasowanie is not None