DROP TABLE Konta;
DROP TABLE Uzytkownicy;
DROP TABLE Transakcje;
DROP TABLE Produkty;
DROP TABLE Karty;

DROP TYPE Adres
DROP TYPE DaneOsobowe
DROP TYPE Konto
DROP TYPE Produkt
DROP TYPE Transakcja
DROP TYPE Karta

IF EXISTS (
    SELECT * FROM sys.assemblies WHERE name = 'UDT_CLR'
)
BEGIN
    DROP ASSEMBLY UDT_CLR;
END