from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import clr
from datetime import datetime

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
    produkty = cursor.fetchall()
    return render_template('home.html', produkty=produkty)

@app.route('/koszyk')
def koszyk_page():
    cursor.execute('Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty')
    produkty = cursor.fetchall()
    koszyk_produktow = [(item[0], item[1], koszyk[i][1]) for i, item in enumerate(produkty) if koszyk[i][0]]

    return render_template('koszyk.html', koszyk_produktow=koszyk_produktow)

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
        print(data_urodzenia)
        numer_telefonu = request.form['Numer telefonu']

        konto = f'{login};{haslo1};{email}'
        dane = f'{imie};{nazwisko};{data_urodzenia};{numer_telefonu};{email}'
        
        # Wykonanie zapytania SQL
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO Konta (Dane, Konto) VALUES (CONVERT(DaneOsobowe, ?), CONVERT(Konto, ?))", (dane, konto))
        cnxn.commit()
        print('Dodano konto!')
        flash('Poprawnie zarejestrowano uzytkownika!', category = 'success')
        return redirect(url_for('logowanie'))
    return render_template('rejestracja.html')

@app.route('/logowanie', methods=['GET', 'POST'])
def logowanie():
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
            return redirect(url_for('logowanie'))
        else:
            flash('Podales nieprawidlowe dane!', category = 'danger')

    return render_template('logowanie.html')

@app.route('/wylogowywanie')
def wylogowywanie():
    logged_in = False
    logged_in_id = -1
    flash('Zostałeś pomyślnie wylogowany(a)!', category='info')
    return redirect(url_for('home_page'))

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
    if request.method == 'POST':
        # Wykonanie zapytania SQL
        cursor.execute('DELETE FROM Adresy WHERE ID=?', id)
        cnxn.commit()
        return 'Usunięto adres!'
    return render_template('usun_adres.html', id=id)

if __name__ == '__main__':
    app.run(debug=True)
