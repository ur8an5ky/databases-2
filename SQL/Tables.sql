CREATE TABLE Konta (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Dane DaneOsobowe,
    Konto Konto
);

CREATE TABLE Uzytkownicy (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Dane DaneOsobowe,
    Adres Adres
);

CREATE TABLE Transakcje (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Transakcja Transakcja,
	IdKonta INT,
	Historia NVARCHAR(4)
);

CREATE TABLE Produkty (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Produkt Produkt
);

CREATE TABLE Karty (
    Karta Karta,
    Konto Konto
);