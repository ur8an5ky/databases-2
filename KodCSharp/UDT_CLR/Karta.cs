using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.Text.RegularExpressions;
using System.IO;
using System.Globalization;
using System.IO.Ports;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzKarte")]
public struct Karta: INullable, IBinarySerialize
{
    private bool is_Null;
    private string _imie;
    private string _nazwisko;
    private string _numerKarty;
    private DateTime _dataWaznosci;
    private string _cvv;
    public bool IsNull
    {
        get
        { return (is_Null); }
    }
    public static Karta Null
    {
        get
        {
            Karta ka = new Karta();
            ka.is_Null = true;
            return ka;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            return $"{_imie} {_nazwisko}, nr {_numerKarty}, wazna do: {_dataWaznosci}, CVV: {_cvv}";

        }
    }
    [SqlMethod(OnNullCall = false)]
    public static Karta Parse(SqlString s)
    {
        if (s.IsNull)
            throw new ArgumentNullException(nameof(s));

        string[] parts = s.Value.Split(';');

        if (parts.Length != 5)
            throw new ArgumentException("Nieprawid³owy format napisu. Oczekiwano: 'imie;nazwisko;numerKarty;dataWaznosci;cvv'");

        Karta ka = new Karta();
        ka.Imie = parts[0];
        ka.Nazwisko = parts[1];
        ka.NumerKarty = parts[2];
        ka.DataWaznosci = DateTime.ParseExact(parts[3], "MM/yyyy", CultureInfo.InvariantCulture);
        ka.CVV = parts[4];

        if (!ka.SprawdzKarte())
            throw new ArgumentException("Nieprawidlowe dane karty.");
        return ka;
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
    public string NumerKarty
    {
        get { return this._numerKarty; }
        set
        {
            string temp = _numerKarty;
            _numerKarty = value;
            if ((string.IsNullOrEmpty(_numerKarty)) || (_numerKarty.Length != 16))
            {
                _numerKarty = temp;
                throw new ArgumentException("Nieprawidlowy numer karty.");
            }
        }
    }
    public DateTime DataWaznosci
    {
        get { return this._dataWaznosci; }
        set
        {
            DateTime temp = _dataWaznosci;
            _dataWaznosci = value;
            if ((_dataWaznosci < DateTime.Today.AddYears(-5).Date) || (_dataWaznosci >= DateTime.Today.AddYears(4).Date))
            {
                _dataWaznosci = temp;
                throw new ArgumentException("Nieprawidlowa data waznosci.");
            }
        }
    }
    public string CVV
    {
        get { return this._cvv; }
        set
        {
            string temp = _cvv;
            _cvv = value;
            if ((string.IsNullOrEmpty(_cvv)) || (_cvv.Length != 3))
            {
                _cvv = temp;
                throw new ArgumentException("Nieprawidlowy numer CVV.");
            }
        }
    }
    private bool SprawdzKarte()
    {
        if ((!string.IsNullOrEmpty(_imie)) && (!string.IsNullOrEmpty(_nazwisko))
            && ((!string.IsNullOrEmpty(_numerKarty)) && (_numerKarty.Length == 16))
            && ((_dataWaznosci >= DateTime.Today.AddYears(-5).Date) && (_dataWaznosci < DateTime.Today.AddYears(4).Date))
            && ((!string.IsNullOrEmpty(_cvv)) && (_cvv.Length == 3)))
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
        _numerKarty = r.ReadString();
        _dataWaznosci = DateTime.FromBinary(r.ReadInt64());
        _cvv = r.ReadString();
    }
    public void Write(BinaryWriter w)
    {
        w.Write(is_Null);
        w.Write(_imie);
        w.Write(_nazwisko);
        w.Write(_numerKarty);
        w.Write(_dataWaznosci.ToBinary());
        w.Write(_cvv);
    }
}