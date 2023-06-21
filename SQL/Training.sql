INSERT INTO Karty (Karta, Konto)
VALUES (CONVERT(Karta, N'Baza;Dana;0000000000000000;01/10/2026;000'), CONVERT(Konto, N'Administrator;Passw0rd;email@baza.dana'));

Select Id, CAST(Dane as NVARCHAR(MAX)), CAST(Konto as NVARCHAR(MAX)) FROM Konta WHERE CAST(Konto as NVARCHAR(MAX)) LIKE '%Administrator%';
Select Id, CAST(Dane as NVARCHAR(MAX)), CAST(Konto as NVARCHAR(MAX)) FROM Konta;
Select CAST(Karta as NVARCHAR(MAX)), CAST(Konto as NVARCHAR(MAX)) FROM Karty;
Select Id, CAST(Dane as NVARCHAR(MAX)), CAST(Adres as NVARCHAR(MAX)) FROM Uzytkownicy;
Select CAST(Transakcja as NVARCHAR(MAX)), IdKonta, Historia FROM Transakcje;
Select Id, CAST(Produkt as NVARCHAR(MAX)) FROM Produkty;
Select Historia FROM Transakcje WHERE IdKonta = 1;