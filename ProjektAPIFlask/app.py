from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)

# Konfiguracja połączenia do bazy danych
server = 'ADRES_SERWERA'
database = 'NAZWA_BAZY_DANYCH'
username = 'UZYTKOWNIK'
password = 'HASLO'
cnxn = pyodbc.connect(f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}')
cursor = cnxn.cursor()

# Ścieżka względna do pliku DLL
dll_path = "..\\KodCSharp\\UDT_CLR\\bin\\Debug\\UDT_CLR.dll"

# Strona główna - wyświetlanie listy klientów
@app.route('/')
def index():
    cursor.execute('SELECT * FROM Klienci')
    klienci = cursor.fetchall()
    return render_template('index.html', klienci=klienci)

# Dodawanie nowego klienta
@app.route('/dodaj', methods=['GET', 'POST'])
def dodaj():
    if request.method == 'POST':
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        # Przygotowanie wartości typu UDT
        klient_udt = f'Klient("{imie}", "{nazwisko}")'
        # Wykonanie zapytania SQL
        cursor.execute(f'INSERT INTO Klienci (Dane) VALUES ({klient_udt})')
        cnxn.commit()
        return 'Dodano klienta!'
    return render_template('dodaj.html')

# Usuwanie klienta
@app.route('/usun/<int:id>', methods=['GET', 'POST'])
def usun(id):
    if request.method == 'POST':
        # Wykonanie zapytania SQL
        cursor.execute(f'DELETE FROM Klienci WHERE ID={id}')
        cnxn.commit()
        return 'Usunięto klienta!'
    return render_template('usun.html', id=id)

if __name__ == '__main__':
    app.run(debug=True)
