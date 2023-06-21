from App import app, cursor, cnxn
from flask import render_template, request, redirect, url_for, flash
from datetime import datetime, date
from App.methods import selects, ustaw_koszyk_default, sprawdz_format_stringa

@app.route('/')
def home_page():
    cursor.execute('Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty')
    produkty_krotki = cursor.fetchall()
    print(produkty_krotki)
    produkty = [list(krotka) for krotka in produkty_krotki]
    for pr in produkty:
        pr[1] = pr[1].split(';')
        print(pr[1])
    return render_template('home.html', produkty=produkty, logged_in=app.config['logged_in'], login=app.config['login'])

@app.route('/koszyk', methods=['GET', 'POST'])
def koszyk_page():
    cursor.execute('Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty')
    produkty_krotki = cursor.fetchall()
    produkty = [list(krotka) for krotka in produkty_krotki]
    cena = 0.0
    id_konta = 0
    if app.config['logged_in_id'] != -1:
        dane, _, _ = selects(app.config['logged_in_id'])
        id_konta = dane[0][0]
    print(id_konta)
    for pr, k in zip(produkty, app.config['koszyk']):
        pr[1] = pr[1].split(';')
        cena += float(pr[1][2].replace(',', '.'))*k[1]
        print(cena)
    koszyk_produktow = [(item[0], item[1], app.config['koszyk'][i][1]) for i, item in enumerate(produkty) if app.config['koszyk'][i][0]]

    karta = []
    if app.config['logged_in']:
        _, _, karta = selects(app.config['logged_in_id'])
        if karta:
            state = karta
        else:
            state = 0
            if request.method == 'POST':
                imie = request.form['Imie']
                nazwisko = request.form['Nazwisko']
                numer_karty = request.form['Numer karty']
                data_waznosci = request.form['Data waznosci']
                cvv = request.form['CVV']
                if len(numer_karty) != 16 or len(cvv) != 3 or not sprawdz_format_stringa(data_waznosci):
                    flash('Podales nieprawidlowe dane karty!', category = 'danger')
                else:
                    return redirect(url_for('logowanie'))
    else:
        state = -1
        if request.method == 'POST':
            imie = request.form['Imie']
            nazwisko = request.form['Nazwisko']
            numer_karty = request.form['Numer karty']
            data_waznosci = request.form['Data waznosci']
            cvv = request.form['CVV']
            if len(numer_karty) != 16 or len(cvv) != 3 or not sprawdz_format_stringa(data_waznosci):
                flash('Podales nieprawidlowe dane karty!', category = 'danger')
            else:
                karta = [numer_karty, data_waznosci]
                state = 1
    return render_template('koszyk.html', koszyk_produktow=koszyk_produktow, cena=cena, state=state, num=1, karta=karta, id_konta=id_konta, logged_in=app.config['logged_in'], login=app.config['login'])

@app.route('/koszyk/potwierdzenie/<int:id_konta>/<float:kwota>', methods=['GET', 'POST'])
def potwierdzenie(id_konta, kwota):
    today = date.today().strftime("%d.%m.%Y")
    kwota = str(kwota).replace('.', ',')
    s = [str(app.config['koszyk'][0][1]),str(app.config['koszyk'][1][1]),str(app.config['koszyk'][2][1]),str(app.config['koszyk'][3][1])]
    historia = f'{s[0]}{s[1]}{s[2]}{s[3]}'
    print(historia)

    cursor = cnxn.cursor()
    cursor.execute("INSERT INTO Transakcje (Transakcja, IdKonta, Historia) VALUES (CONVERT(Transakcja, ?), ?, ?)", (f'{kwota};{today}', id_konta, historia))
    cnxn.commit()

    ilosci = [k[1] for k in app.config['koszyk']]
    cursor.execute('Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty')
    produkty = cursor.fetchall()
    string_na_listy = []
    for produkt, ilosc in zip(produkty, ilosci):
        sublist = produkt[1].split(';')
        sublist[-1] = int(sublist[-1]) - ilosc
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

    ustaw_koszyk_default()
    return render_template('potwierdzenie.html', logged_in=app.config['logged_in'], login=app.config['login'])

@app.route('/dodaj_do_koszyka/<int:produkt_id>', methods=['POST'])
def dodaj_do_koszyka(produkt_id):
    index = produkt_id - 1

    app.config['koszyk'][index] = (True, 1)

    flash('Dodano artykuł do koszyka.', category='success')
    print(app.config['koszyk'])
    return redirect(url_for('home_page'))

@app.route('/zmien_liczbe/<int:produkt_id>', methods=['POST'])
def zmien_liczbe(produkt_id):
    index = produkt_id - 1

    aktualna_liczba = app.config['koszyk'][index][1]

    if request.form['submit_button'] == 'dodaj':
        nowa_liczba = min(aktualna_liczba + 1, 10)
    else:
        nowa_liczba = max(aktualna_liczba - 1, 0)

    app.config['koszyk'][index] = (True, nowa_liczba)
    if nowa_liczba == 0:
        app.config['koszyk'][index] = (False, nowa_liczba)
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
        numer_telefonu = request.form['Numer telefonu']

        ulica = request.form['Ulica']
        numer_domu = request.form['Numer domu']
        miasto = request.form['Miasto']
        kod_pocztowy = request.form['Kod pocztowy']
        kraj = request.form['Kraj']

        konto = f'{login};{haslo1};{email}'
        dane = f'{imie};{nazwisko};{data_urodzenia};{numer_telefonu};{email}'
        adres = f'{ulica};{numer_domu};{miasto};{kod_pocztowy};{kraj}'
        
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
    return render_template('rejestracja.html', logged_in=app.config['logged_in'], login=app.config['login'])

@app.route('/logowanie', methods=['GET', 'POST'])
def logowanie():
    if request.method == 'POST':
        login = request.form['Login']
        haslo = request.form['Haslo']
        
        cursor = cnxn.cursor()
        cursor.execute("Select Id, CAST(Dane as NVARCHAR(MAX)), CAST(Konto as NVARCHAR(MAX)) FROM Konta WHERE CAST(Konto as NVARCHAR(MAX)) LIKE ?", (f'{login};{haslo};%',))
        row = cursor.fetchone()
        print(row)

        if row:
            dane = row[1]
            konto = row[2]
            
            dane_osobowe = dane.split(';')
            imie = dane_osobowe[0]
            nazwisko = dane_osobowe[1]
            data_urodzenia = dane_osobowe[2]
            numer_telefonu = dane_osobowe[3]
            email = dane_osobowe[4]
            
            print('Zalogowano pomyślnie!')
            print(f"Imię: {imie}")
            print(f"Nazwisko: {nazwisko}")
            print(f"Data urodzenia: {data_urodzenia}")
            print(f"Numer telefonu: {numer_telefonu}")
            print(f"Email: {email}")
            
            flash(f'Jestes zalogowany jako {login}!', category = 'success')
            app.config['logged_in'] = True
            app.config['logged_in_id'] = row[0]
            app.config['login'] = login
            print(app.config['logged_in_id'])
            return redirect(url_for('dane'))
        else:
            flash('Podales nieprawidlowe dane!', category = 'danger')

    return render_template('logowanie.html', logged_in=app.config['logged_in'], login=app.config['login'])

@app.route('/wylogowywanie')
def wylogowywanie():
    app.config['logged_in'] = False
    app.config['logged_in_id'] = -1
    app.config['login'] = ''
    ustaw_koszyk_default()
    print(app.config['koszyk'])
    flash('Zostałeś pomyślnie wylogowany(a)!', category='info')
    return redirect(url_for('home_page'))

@app.route('/dane')
def dane():
    dane, adres, karta = selects(app.config['logged_in_id'])

    dane = [list(krotka) for krotka in dane]
    dane[0][1] = dane[0][1].replace(" 00:00:00", "").split(';')
    dane[0][2] = dane[0][2].split(';')

    adres = [list(krotka) for krotka in adres]
    adres = adres[0][2].split(';')

    print(app.config['logged_in_id'])
    transakcje = []
    zakupy = []
    produkty = []
    tbool = False
    s = app.config['logged_in_id']
    cursor.execute(f'Select CAST(Transakcja as NVARCHAR(MAX)), Historia FROM Transakcje WHERE IdKonta = {s}')
    transakcje = cursor.fetchall()
    print(transakcje)
    if transakcje:
        zakupy = [transakcja[1] for transakcja in transakcje]
        transakcje = [transakcja[0].split(';') for transakcja in transakcje]
        tbool = True
        print(transakcje)
        cursor.execute('Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty')
        produkty_krotki = cursor.fetchall()
        print(produkty_krotki)
        produkty = [list(krotka) for krotka in produkty_krotki]
        for pr in produkty:
            pr[1] = pr[1].split(';')
            print(pr[1])
        result = []
        for sublist in produkty:
            result.append(' '.join(sublist[1]))
        produkty = result

    kbool = False
    if karta:
        kbool = True

    return render_template('dane.html', dane=dane, adres=adres, karta=karta, kbool=kbool, transakcje=transakcje, tbool=tbool, produkty=produkty, zakupy=zakupy, num=0, zip=zip, enumerate=enumerate, logged_in=app.config['logged_in'], login=app.config['login'])

@app.route('/dodaj_karte/<int:redirect_type>', methods=['GET', 'POST'])
def dodaj_karte(redirect_type):
    print(app.config['logged_in_id'])
    cursor = cnxn.cursor()
    s = app.config['logged_in_id']
    cursor.execute(f'Select CAST(Konto as NVARCHAR(MAX)) FROM Konta WHERE Id = {s}')
    konto = cursor.fetchall()[0][0]

    if request.method == 'POST':
        imie = request.form['Imie']
        nazwisko = request.form['Nazwisko']
        numer_karty = request.form['Numer karty']
        data_waznosci = "01/" + request.form['Data waznosci']
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
    return render_template('dodaj_karte.html', redirect_type=redirect_type, logged_in=app.config['logged_in'], login=app.config['login'])