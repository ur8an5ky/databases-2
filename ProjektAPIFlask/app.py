from flask import Flask, render_template, request
import pyodbc
import clr
from datetime import datetime

app = Flask(__name__)

# Konfiguracja połączenia do bazy danych
server = 'LAPTOP-OSQFQF1M\SQLEXPRESS'
database = 'UDT_CLR'
# username = 'UZYTKOWNIK'
# password = 'HASLO'
cnxn = pyodbc.connect(f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes')
cursor = cnxn.cursor()

# Ścieżka względna do pliku DLL
dll_path = "..\\KodCSharp\\UDT_CLR\\bin\\Debug\\UDT_CLR.dll"

# Ładowanie pliku DLL
# clr.AddReference(dll_path)
# from KodCHarp.UDT_CLR import Klient, Adres

# Strona główna - wyświetlanie listy klientów
@app.route('/')
def home_page():
    cursor.execute('SELECT * FROM Adresy')
    adresy = cursor.fetchall()
    return render_template('home.html', adresy=adresy)

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
        return 'Dodano konto!'
    return render_template('rejestracja.html')

# Dodawanie nowy adres
@app.route('/dodaj_adres', methods=['GET', 'POST'])
def dodaj_adres():
    if request.method == 'POST':
        ulica = request.form['Ulica']
        numer_domu = request.form['Numer domu']
        # numer_mieszkania = request.form['numer_mieszkania']
        miasto = request.form['Miasto']
        kod_pocztowy = request.form['Kod pocztowy']
        kraj = request.form['Kraj']
        # Tworzenie obiektu typu Adres w Pythonie
        adres = f'ul. {ulica} {numer_domu}, {miasto} {kod_pocztowy}, {kraj}'
        
        # Wykonanie zapytania SQL
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO Adresy (Adres) VALUES (?)", adres)
        cnxn.commit()
        return 'Dodano adres!'
    return render_template('dodaj_adres.html')

# Usuwanie adresu
@app.route('/usun_adres/<int:id>', methods=['GET', 'POST'])
def usun_adres(id):
    if request.method == 'POST':
        # Wykonanie zapytania SQL
        cursor.execute('DELETE FROM Adresy WHERE ID=?', id)
        cnxn.commit()
        return 'Usunięto adres!'
    return render_template('usun_adres.html', id=id)

if __name__ == '__main__':
    app.run(debug=True)
