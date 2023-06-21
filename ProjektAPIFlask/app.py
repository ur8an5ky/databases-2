from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import clr
from datetime import datetime, date
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = '2493b92811db16ce03a76959'

# Konfiguracja połączenia do bazy danych
server = 'LAPTOP-OSQFQF1M\SQLEXPRESS'
database = 'UDT_CLR'
# username = 'UZYTKOWNIK'
# password = 'HASLO'
cnxn = pyodbc.connect(f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes')
cursor = cnxn.cursor()

logged_in = False
logged_in_id = -1
koszyk = [(False, 0), (False, 0), (False, 0), (False, 0)]

def ustaw_koszyk_default(koszyk):
    for i in range(len(koszyk)):
        koszyk[i] = (False, 0)

# Ścieżka względna do pliku DLL
dll_path = "..\\KodCSharp\\UDT_CLR\\bin\\Debug\\UDT_CLR.dll"

# Ładowanie pliku DLL
# clr.AddReference(dll_path)
# from KodCHarp.UDT_CLR import Klient, Adres

# Strona główna - wyświetlanie listy klientów
@app.route('/')
def home_page():
    cursor.execute('Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty')
    produkty_krotki = cursor.fetchall()
    print(produkty_krotki)
    produkty = [list(krotka) for krotka in produkty_krotki]
    for pr in produkty:
        pr[1] = pr[1].split(';')
        print(pr[1])
    # print(produkty)
    # produkty = produkty_krotki.strip()
    return render_template('home.html', produkty=produkty)

@app.route('/koszyk', methods=['GET', 'POST'])
def koszyk_page():
    global koszyk, logged_in, logged_in_id
    cursor.execute('Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty')
    produkty_krotki = cursor.fetchall()
    produkty = [list(krotka) for krotka in produkty_krotki]
    cena = 0.0
    id_konta = 0
    if logged_in_id != -1:
        dane, _, _ = fun(logged_in_id)
        id_konta = dane[0][0]
    print(id_konta)
    for pr, k in zip(produkty, koszyk):
        pr[1] = pr[1].split(';')
        cena += float(pr[1][2].replace(',', '.'))*k[1]
        print(cena)
    koszyk_produktow = [(item[0], item[1], koszyk[i][1]) for i, item in enumerate(produkty) if koszyk[i][0]]

    karta = []
    if logged_in:
        _, _, karta = fun(logged_in_id)
        if karta:
            state = karta
        else:
            state = 0
            if request.method == 'POST':
                imie = request.form['Imie']
                nazwisko = request.form['Nazwisko']
                numer_karty = request.form['Numer karty']
                data_waznosci = request.form['Data waznosci']   # tylko miesiąc i rok
                cvv = request.form['CVV']
                if len(numer_karty) != 16 or len(cvv) != 3 or not sprawdz_forme_stringa(data_waznosci):
                    flash('Podales nieprawidlowe dane karty!', category = 'danger')
                else:
                    return redirect(url_for('logowanie'))
    else:
        state = -1
        if request.method == 'POST':
            imie = request.form['Imie']
            nazwisko = request.form['Nazwisko']
            numer_karty = request.form['Numer karty']
            data_waznosci = request.form['Data waznosci']   # tylko miesiąc i rok
            cvv = request.form['CVV']
            if len(numer_karty) != 16 or len(cvv) != 3 or not sprawdz_forme_stringa(data_waznosci):
                flash('Podales nieprawidlowe dane karty!', category = 'danger')
            else:
                karta = [numer_karty, data_waznosci]
                state = 1
                # return redirect(url_for('logowanie'))
    return render_template('koszyk.html', koszyk_produktow=koszyk_produktow, cena=cena, state=state, num=1, karta=karta, id_konta=id_konta)


@app.route('/koszyk/potwierdzenie/<int:id_konta>/<float:kwota>', methods=['GET', 'POST'])
def potwierdzenie(id_konta, kwota):
    global koszyk
    today = date.today().strftime("%d.%m.%Y")
    print(today, type(today))
    print(id_konta, type(id_konta))
    print(kwota, type(kwota))
    kwota = str(kwota).replace('.', ',')

    cursor = cnxn.cursor()
    cursor.execute("INSERT INTO Transakcje (Transakcja, IdKonta) VALUES (CONVERT(Transakcja, ?), ?)", (f'{kwota};{today}', id_konta))
    cnxn.commit()

    ilosci = [k[1] for k in koszyk]
    cursor.execute('Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty')
    produkty = cursor.fetchall()
    string_na_listy = []
    for produkt, ilosc in zip(produkty, ilosci):
        sublist = produkt[1].split(';')  # Podział stringu na elementy oddzielone średnikiem
        sublist[-1] = int(sublist[-1]) - ilosc  # Konwersja ostatniego elementu na int
        string_na_listy.append(sublist)
    print(string_na_listy)
    listy_na_string = []
    for sublist in string_na_listy:
        joined_string = ';'.join(str(item) for item in sublist)
        listy_na_string.append(joined_string)
    print(listy_na_string)
    for i in range(4):
        cursor = cnxn.cursor()
        cursor.execute("UPDATE Produkty SET Produkt = CONVERT(Produkt, ?) WHERE Id = ?", (listy_na_string[i],i+1))
        cnxn.commit()

    ustaw_koszyk_default(koszyk)
    return render_template('potwierdzenie.html')


@app.route('/dodaj_do_koszyka/<int:produkt_id>', methods=['POST'])
def dodaj_do_koszyka(produkt_id):
    global logged_in, logged_in_id

    index = produkt_id - 1

    koszyk[index] = (True, 1)

    flash('Dodano artykuł do koszyka.')
    print(koszyk)
    return redirect(url_for('home_page'))

@app.route('/zmien_liczbe/<int:produkt_id>', methods=['POST'])
def zmien_liczbe(produkt_id):
    global koszyk

    # Znajdowanie indeksu produktu w liście koszyka na podstawie produkt_id
    index = produkt_id - 1

    # Pobranie aktualnej liczby artykułów dla danego produktu
    aktualna_liczba = koszyk[index][1]

    # Sprawdzenie, czy przycisk dodawania czy odejmowania został kliknięty
    if request.form['submit_button'] == 'dodaj':
        # Zwiększenie liczby artykułów o 1 (z ograniczeniem do maksymalnie 10)
        nowa_liczba = min(aktualna_liczba + 1, 10)
    else:
        # Zmniejszenie liczby artykułów o 1 (z ograniczeniem do minimalnie 0)
        nowa_liczba = max(aktualna_liczba - 1, 0)

    # Aktualizacja liczby artykułów w koszyku
    koszyk[index] = (True, nowa_liczba)
    if nowa_liczba == 0:
        koszyk[index] = (False, nowa_liczba)
    return redirect(url_for('koszyk_page'))

@app.route('/rejestracja', methods=['GET', 'POST'])
def rejestracja():
    if request.method == 'POST':
        login = request.form['Login']
        email = request.form['Email']
        haslo1 = request.form['Haslo1']
        haslo2 = request.form['Haslo2']

        imie = request.form['Imie']
        nazwisko = request.form['Nazwisko']
        data_urodzenia = datetime.strptime(request.form['Data urodzenia'], "%Y-%m-%d").strftime("%d.%m.%Y")
        # print(data_urodzenia)
        numer_telefonu = request.form['Numer telefonu']

        ulica = request.form['Ulica']
        numer_domu = request.form['Numer domu']
        miasto = request.form['Miasto']
        kod_pocztowy = request.form['Kod pocztowy']
        kraj = request.form['Kraj']

        konto = f'{login};{haslo1};{email}'
        dane = f'{imie};{nazwisko};{data_urodzenia};{numer_telefonu};{email}'
        adres = f'{ulica};{numer_domu};{miasto};{kod_pocztowy};{kraj}'
        
        # Wykonanie zapytania SQL
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO Konta (Dane, Konto) VALUES (CONVERT(DaneOsobowe, ?), CONVERT(Konto, ?))", (dane, konto))
        cnxn.commit()
        print('Dodano konto!')
        flash('Poprawnie zarejestrowano uzytkownika!', category = 'success')

        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO Uzytkownicy (Dane, Adres) VALUES (CONVERT(DaneOsobowe, ?), CONVERT(Adres, ?))", (dane, adres))
        cnxn.commit()
        print('Dodano poprawny adres!')
        flash('Poprawnie dodano adres!', category = 'success')
        return redirect(url_for('logowanie'))
    return render_template('rejestracja.html')

@app.route('/logowanie', methods=['GET', 'POST'])
def logowanie():
    global logged_in_id, logged_in
    if request.method == 'POST':
        login = request.form['Login']
        haslo = request.form['Haslo']
        
        # Wykonanie zapytania SQL
        cursor = cnxn.cursor()
        cursor.execute("Select Id, CAST(Dane as NVARCHAR(MAX)), CAST(Konto as NVARCHAR(MAX)) FROM Konta WHERE CAST(Konto as NVARCHAR(MAX)) LIKE ?", (f'{login};{haslo};%',))
        row = cursor.fetchone()
        print(row)

        if row:
            dane = row[1]
            konto = row[2]
            
            # Przetwarzanie danych UDT
            dane_osobowe = dane.split(';')
            imie = dane_osobowe[0]
            nazwisko = dane_osobowe[1]
            data_urodzenia = dane_osobowe[2]
            numer_telefonu = dane_osobowe[3]
            email = dane_osobowe[4]
            
            # Wyświetlanie informacji
            print('Zalogowano pomyślnie!')
            print(f"Imię: {imie}")
            print(f"Nazwisko: {nazwisko}")
            print(f"Data urodzenia: {data_urodzenia}")
            print(f"Numer telefonu: {numer_telefonu}")
            print(f"Email: {email}")
            
            flash('Jestes zalogowany jako Admin!', category = 'success')
            logged_in = True
            logged_in_id = row[0]
            print(logged_in_id)
            return redirect(url_for('dane'))
        else:
            flash('Podales nieprawidlowe dane!', category = 'danger')

    return render_template('logowanie.html')

@app.route('/wylogowywanie')
def wylogowywanie():
    global logged_in, logged_in_id, koszyk
    logged_in = False
    logged_in_id = -1
    ustaw_koszyk_default(koszyk)
    print(koszyk)
    flash('Zostałeś pomyślnie wylogowany(a)!', category='info')
    return redirect(url_for('home_page'))

@app.route('/dane')
def dane():
    global logged_in_id

    dane, adres, karta = fun(logged_in_id)

    dane = [list(krotka) for krotka in dane]
    dane[0][1] = dane[0][1].replace(" 00:00:00", "").split(';')
    dane[0][2] = dane[0][2].split(';')

    adres = [list(krotka) for krotka in adres]
    adres = adres[0][2].split(';')

    kbool = False
    if karta:
        kbool = True

    return render_template('dane.html', dane=dane, adres=adres, karta=karta, kbool=kbool, num=0)

@app.route('/dodaj_karte/<int:redirect_type>', methods=['GET', 'POST'])
def dodaj_karte(redirect_type):
    global logged_in_id
    print(logged_in_id)
    cursor = cnxn.cursor()
    cursor.execute(f'Select CAST(Konto as NVARCHAR(MAX)) FROM Konta WHERE Id = {logged_in_id}')
    konto = cursor.fetchall()[0][0]

    if request.method == 'POST':
        imie = request.form['Imie']
        nazwisko = request.form['Nazwisko']
        numer_karty = request.form['Numer karty']
        data_waznosci = "01/" + request.form['Data waznosci']   # tylko miesiąc i rok
        cvv = request.form['CVV']

        karta = f'{imie};{nazwisko};{numer_karty};{data_waznosci};{cvv}'
        print(karta)

        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO Karty (Karta, Konto) VALUES (CONVERT(Karta, ?), CONVERT(Konto, ?))", (karta, konto))
        cnxn.commit()
        print('Dodano karte!')
        flash('Poprawnie dodano dane karty!', category = 'success')
        if redirect_type == 0:
            return redirect(url_for('dane'))
        elif redirect_type == 1:
            return redirect(url_for('koszyk_page'))
    return render_template('dodaj_karte.html', redirect_type=redirect_type)
    
# Dodawanie nowy adres
# @app.route('/dodaj_adres', methods=['GET', 'POST'])
# def dodaj_adres():
#     if request.method == 'POST':
#         ulica = request.form['Ulica']
#         numer_domu = request.form['Numer domu']
#         # numer_mieszkania = request.form['numer_mieszkania']
#         miasto = request.form['Miasto']
#         kod_pocztowy = request.form['Kod pocztowy']
#         kraj = request.form['Kraj']
#         # Tworzenie obiektu typu Adres w Pythonie
#         adres = f'ul. {ulica} {numer_domu}, {miasto} {kod_pocztowy}, {kraj}'
        
#         # Wykonanie zapytania SQL
#         cursor = cnxn.cursor()
#         cursor.execute("INSERT INTO Adresy (Adres) VALUES (?)", adres)
#         cnxn.commit()
#         return 'Dodano adres!'
#     return render_template('dodaj_adres.html')

# # Usuwanie adresu
# @app.route('/usun_adres/<int:id>', methods=['GET', 'POST'])
# def usun_adres(id):
#     if request.method == 'POST':
#         # Wykonanie zapytania SQL
#         cursor.execute('DELETE FROM Adresy WHERE ID=?', id)
#         cnxn.commit()
#         return 'Usunięto adres!'
#     return render_template('usun_adres.html', id=id)

def fun(id):
    cursor.execute(f'Select Id, CAST(Dane as NVARCHAR(MAX)), CAST(Konto as NVARCHAR(MAX)) FROM Konta WHERE Id = {logged_in_id}')
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

def sprawdz_forme_stringa(string):
    wzor = r'^(0[1-9]|1[0-2])/20(23|24|25|26|27)$'
    dopasowanie = re.match(wzor, string)
    return dopasowanie is not None

if __name__ == '__main__':
    app.run(debug=True)
