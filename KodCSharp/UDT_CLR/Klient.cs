using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.Text.RegularExpressions;
using System.IO;
using System.Globalization;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
    IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzKlienta")]
public struct Klient : INullable, IBinarySerialize
{
    private bool is_Null;
    private string _imie;
    private string _nazwisko;
    private DateTime _dataUrodzenia;
    private string _numerTelefonu;
    private string _adresEmail;
    private Adres _adres;
    public bool IsNull
    {
        get { return is_Null; }
    }
    public static Klient Null
    {
        get
        {
            Klient kl = new Klient();
            kl.is_Null = true;
            return kl;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            StringBuilder builder = new StringBuilder();
            builder.Append(_imie);
            builder.Append(_nazwisko);
            builder.Append(", ur. ");
            builder.Append(_dataUrodzenia);
            builder.Append("r., tel.: ");
            builder.Append(_numerTelefonu);
            builder.Append(", e-mail: ");
            builder.Append(_adresEmail);
            builder.Append(", ");
            builder.Append(_adres);
            return builder.ToString();
        }
    }
    [SqlMethod(OnNullCall = false)]
    public static Klient Parse(SqlString s)
    {
        if (s.IsNull)
            return Null;
        Klient kl = new Klient();
        string[] xy = s.Value.Split(",".ToCharArray());
        string imieINazwisko = xy[0];
        int pierwszaSpacja = imieINazwisko.IndexOf(' ');
        kl.Imie = imieINazwisko.Substring(0, pierwszaSpacja);
        kl.Nazwisko = imieINazwisko.Substring(pierwszaSpacja + 1);

        string dataUrodzenia = xy[1].Replace("ur.:", "").TrimStart().Replace("r.", "");
        kl.DataUrodzenia = DateTime.ParseExact(dataUrodzenia, "dd.MM.yyyy", CultureInfo.InvariantCulture);
        kl.NumerTelefonu = xy[2].Replace("tel.:", "").TrimStart();
        kl.AdresEmail = xy[3].Replace("e-mail:", "").TrimStart();
        kl.Adres = Adres.Parse(xy[4]);


        if (!kl.SprawdzKlienta())
            throw new ArgumentException("Nieprawid這wy klient.");
        return kl;
    }
    public string Imie
    {
        get { return this._imie; }
        set
        {
            string temp = _imie;
            _imie = value;
            if (!SprawdzKlienta())
            {
                _imie = temp;
                throw new ArgumentException("Nieprawid這we imie.");
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
            if (!SprawdzKlienta())
            {
                _nazwisko = temp;
                throw new ArgumentException("Nieprawid這wy nazwisko.");
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
            if (!SprawdzKlienta())
            {
                _dataUrodzenia = temp;
                throw new ArgumentException("Nieprawid這wa data urodzenia.");
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
            if (!SprawdzKlienta())
            {
                _numerTelefonu = temp;
                throw new ArgumentException("Nieprawid這wy numer telefonu.");
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
            if (!SprawdzKlienta())
            {
                _adresEmail = temp;
                throw new ArgumentException("Nieprawid這wy adres e-mail.");
            }
        }
    }
    public Adres Adres
    {
        get { return this._adres; }
        set
        {
            Adres temp = _adres;
            _adres = value;
            if (!SprawdzKlienta())
            {
                _adres = temp;
                throw new ArgumentException("Nieprawid這wy adres e-mail.");
            }
        }
    }
    private bool SprawdzKlienta()
    {
        string wzorzec = @"^[\w\.-]+@[\w\.-]+\.\w+$";
        Regex regex = new Regex(wzorzec);
        bool email = regex.IsMatch(_adresEmail);
        if ((string.IsNullOrEmpty(_imie)) && (string.IsNullOrEmpty(_nazwisko))
            && ((_dataUrodzenia >= new DateTime(1900, 1, 1)) && (_dataUrodzenia < DateTime.Today))
            && ((string.IsNullOrEmpty(_numerTelefonu)) && (_numerTelefonu.Length == 9))
            && ((string.IsNullOrEmpty(_adresEmail)) && (email)))
        {
            return true;
        }
        else
        {
            return false;
        }
        return true;
    }
    public void Read(BinaryReader r)
    {
        is_Null = r.ReadBoolean();
        _imie = r.ReadString();
        _nazwisko = r.ReadString();
        _dataUrodzenia = DateTime.FromBinary(r.ReadInt64());
        _numerTelefonu = r.ReadString();
        _adresEmail = r.ReadString();
        _adres.Read(r);
    }
    public void Write(BinaryWriter w)
    {
        w.Write(is_Null);
        w.Write(_imie);
        w.Write(_nazwisko);
        w.Write(_dataUrodzenia.ToBinary());
        w.Write(_numerTelefonu);
        w.Write(_adresEmail);
        _adres.Write(w);
    }
}