using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.Text.RegularExpressions;
using System.IO;
using System.Globalization;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
    IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzDaneOsobowe")]
public struct DaneOsobowe : INullable, IBinarySerialize
{
    private bool is_Null;
    private string _imie;
    private string _nazwisko;
    private DateTime _dataUrodzenia;
    private string _numerTelefonu;
    private string _adresEmail;
    public bool IsNull
    {
        get { return is_Null; }
    }
    public static DaneOsobowe Null
    {
        get
        {
            DaneOsobowe dane = new DaneOsobowe();
            dane.is_Null = true;
            return dane;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            return $"{_imie};{_nazwisko};{_dataUrodzenia};{_numerTelefonu};{_adresEmail}";
        }
    }
    [SqlMethod(OnNullCall = false)]
    public static DaneOsobowe Parse(SqlString s)
    {
        if (s.IsNull)
            throw new ArgumentNullException(nameof(s));

        string[] parts = s.Value.Split(';');

        if (parts.Length != 5)
            throw new ArgumentException("Nieprawid³owy format napisu. Oczekiwano: 'imie;nazwisko;dataUrodzenia;numerTelefonu;adresEmail'");

        DaneOsobowe dane = new DaneOsobowe();
        dane.Imie = parts[0];
        dane.Nazwisko = parts[1];
        dane.DataUrodzenia = DateTime.ParseExact(parts[2], "dd.MM.yyyy", CultureInfo.InvariantCulture);
        dane.NumerTelefonu = parts[3];
        dane.AdresEmail = parts[4];

        if (!dane.SprawdzDaneOsobowe())
            throw new ArgumentException("Nieprawidlowe dane osobowe.");
        return dane;
    }
    public string Imie
    {
        get { return this._imie; }
        set
        {
            string temp = _imie;
            _imie = value;
            if (string.IsNullOrEmpty(_imie))
            {
                _imie = temp;
                throw new ArgumentException("Nieprawidlowe imie.");
            }
        }
    }
    public string Nazwisko
    {
        get { return this._nazwisko; }
        set
        {
            string temp = _nazwisko;
            _nazwisko = value;
            if (string.IsNullOrEmpty(_nazwisko))
            {
                _nazwisko = temp;
                throw new ArgumentException("Nieprawidlowy nazwisko.");
            }
        }
    }
    public DateTime DataUrodzenia
    {
        get { return this._dataUrodzenia; }
        set
        {
            DateTime temp = _dataUrodzenia;
            _dataUrodzenia = value;
            if ((_dataUrodzenia < new DateTime(1900, 1, 1)) || (_dataUrodzenia > DateTime.Today))
            {
                _dataUrodzenia = temp;
                throw new ArgumentException("Nieprawidlowa data urodzenia.");
            }
        }
    }
    public string NumerTelefonu
    {
        get { return this._numerTelefonu; }
        set
        {
            string temp = _numerTelefonu;
            _numerTelefonu = value;
            if (string.IsNullOrEmpty(_numerTelefonu) || _numerTelefonu.Length != 9)
            {
                _numerTelefonu = temp;
                throw new ArgumentException("Nieprawidlowy numer telefonu.");
            }
        }
    }
    public string AdresEmail
    {
        get { return this._adresEmail; }
        set
        {
            string temp = _adresEmail;
            _adresEmail = value;

            string wzorzec = @"^[\w\.-]+@[\w\.-]+\.\w+$";
            Regex regex = new Regex(wzorzec);
            bool email = regex.IsMatch(_adresEmail);
            if (string.IsNullOrEmpty(_adresEmail) || !email)
            {
                _adresEmail = temp;
                throw new ArgumentException("Nieprawidlowy adres e-mail.");
            }
        }
    }
    private bool SprawdzDaneOsobowe()
    {
        string wzorzec = @"^[\w\.-]+@[\w\.-]+\.\w+$";
        Regex regex = new Regex(wzorzec);
        bool email = regex.IsMatch(_adresEmail);
        if ((!string.IsNullOrEmpty(_imie)) && (!string.IsNullOrEmpty(_nazwisko))
            && ((_dataUrodzenia >= new DateTime(1900, 1, 1)) && (_dataUrodzenia < DateTime.Today))
            && ((!string.IsNullOrEmpty(_numerTelefonu)) && (_numerTelefonu.Length == 9))
            && ((!string.IsNullOrEmpty(_adresEmail)) && (email)))
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    public void Read(BinaryReader r)
    {
        is_Null = r.ReadBoolean();
        _imie = r.ReadString();
        _nazwisko = r.ReadString();
        _dataUrodzenia = DateTime.FromBinary(r.ReadInt64());
        _numerTelefonu = r.ReadString();
        _adresEmail = r.ReadString();
    }
    public void Write(BinaryWriter w)
    {
        w.Write(is_Null);
        w.Write(_imie);
        w.Write(_nazwisko);
        w.Write(_dataUrodzenia.ToBinary());
        w.Write(_numerTelefonu);
        w.Write(_adresEmail);
    }
}