using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.IO;
using System.Globalization;
using System.Text.RegularExpressions;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzKonto")]
public struct Konto : INullable, IBinarySerialize
{
    private bool is_Null;
    private string _login;
    private string _haslo;
    private string _adresEmail;
    public bool IsNull
    {
        get
        { return (is_Null); }
    }
    public static Konto Null
    {
        get
        {
            Konto ko = new Konto();
            ko.is_Null = true;
            return ko;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            return $"login: {_login}, haslo: {_haslo}, e-mail: {_adresEmail}";
        }
    }
    [SqlMethod(OnNullCall = false)]
    public static Konto Parse(SqlString s)
    {
        if (s.IsNull)
            throw new ArgumentNullException(nameof(s));

        string[] parts = s.Value.Split(';');

        if (parts.Length != 3)
            throw new ArgumentException("Nieprawid³owy format napisu. Oczekiwano: 'login;haslo;e-mail'");

        Konto ko = new Konto();
        ko.Login = parts[0];
        ko.Haslo = parts[1];
        ko.AdresEmail = parts[2];

        if (!ko.SprawdzKonto())
            throw new ArgumentException("Nieprawidlowe dane konta.");
        return ko;
    }
    public string Login
    {
        get
        { return this._login; }
        set
        {
            string temp = _login;
            _login = value;
            if (string.IsNullOrEmpty(_login))
            {
                _login = temp; throw new ArgumentException("Zly login.");
            }
        }
    }
    public string Haslo
    {
        get
        { return this._haslo; }
        set
        {
            string temp = _haslo;
            _haslo = value;
            if (string.IsNullOrEmpty(_haslo))
            {
                _haslo = temp;
                throw new ArgumentException("Bledne haslo.");
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
    private bool SprawdzKonto()
    {
        string wzorzec = @"^[\w\.-]+@[\w\.-]+\.\w+$";
        Regex regex = new Regex(wzorzec);
        bool email = regex.IsMatch(_adresEmail);
        if ((!string.IsNullOrEmpty(_login)) && (!string.IsNullOrEmpty(_haslo))
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
        _login = r.ReadString();
        _haslo = r.ReadString();
        _adresEmail = r.ReadString();
    }
    public void Write(BinaryWriter w)
    {
        w.Write(is_Null);
        w.Write(_login);
        w.Write(_haslo);
        w.Write(_adresEmail);
    }
}