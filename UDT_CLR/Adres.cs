using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.IO;
using System.Runtime.InteropServices;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzAdres")]
public struct Adres : INullable, IBinarySerialize
{
    private bool is_Null;
    private string _ulica;
    private Int32 _numerDomu;
    private string _miasto;
    private string _kodPocztowy;
    private string _kraj;
    public bool IsNull
    {
        get
        { return (is_Null); }
    }
    public static Adres Null
    {
        get
        {
            Adres ad = new Adres();
            ad.is_Null = true;
            return ad;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            return $"ul. {_ulica} {_numerDomu}, {_miasto} {_kodPocztowy}, {_kraj}";
        }
    }
    [SqlMethod(OnNullCall = false)]
    public static Adres Parse(SqlString s)
    {
        if (s.IsNull)
            throw new ArgumentNullException(nameof(s));

        string[] parts = s.Value.Split(';');

        if (parts.Length != 5)
            throw new ArgumentException("Nieprawid³owy format napisu. Oczekiwano: 'ulica;numerDomu;miasto;kodPocztowy;kraj'");

        Adres ad = new Adres();
        ad.Ulica = parts[0];
        ad.NumerDomu = Int32.Parse(parts[1]);
        ad.Miasto = parts[2];
        ad.KodPocztowy = parts[3];
        ad.Kraj = parts[4];
        if (!ad.SprawdzAdres())
            throw new ArgumentException("Nieprawidlowy adres.");
        return ad;
    }
    public string Ulica
    {
        get
        { return this._ulica; }
        set
        {
            string temp = _ulica;
            _ulica = value;
            if (string.IsNullOrEmpty(_ulica))
            {
                _ulica = temp; throw new ArgumentException("Zla nazwa ulicy.");
            }
        }
    }
    public Int32 NumerDomu
    {
        get
        { return this._numerDomu; }
        set
        {
            Int32 temp = _numerDomu;
            _numerDomu = value;
            if (_numerDomu <= 0)
            {
                _numerDomu = temp;
                throw new ArgumentException("Zla wspolrzedna X.");
            }
        }
    }
    public string KodPocztowy
    {
        get
        { return this._kodPocztowy; }
        set
        {
            string temp = _kodPocztowy;
            _kodPocztowy = value;
            if (string.IsNullOrEmpty(_kodPocztowy))
            {
                _kodPocztowy = temp; throw new ArgumentException("Zly kod pocztowy.");
            }
        }
    }
    public string Miasto
    {
        get
        { return this._miasto; }
        set
        {
            string temp = _miasto;
            _miasto = value;
            if (string.IsNullOrEmpty(_miasto))
            {
                _miasto = temp; throw new ArgumentException("Zla nazwa miasta.");
            }
        }
    }
    public string Kraj
    {
        get
        { return this._kraj; }
        set
        {
            string temp = _kraj;
            _kraj = value;
            if (string.IsNullOrEmpty(_kraj))
            {
                _kraj = temp; throw new ArgumentException("Zla nazwa kraju.");
            }
        }
    }
    private bool SprawdzAdres()
    {
        if ((!string.IsNullOrEmpty(_ulica)) && (_numerDomu > 0)
                && (!string.IsNullOrEmpty(_miasto)) && (!string.IsNullOrEmpty(_kodPocztowy))
                && (!string.IsNullOrEmpty(_kraj)))
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
        _ulica = r.ReadString();
        _numerDomu = r.ReadInt32();
        _miasto = r.ReadString();
        _kodPocztowy = r.ReadString();
        _kraj = r.ReadString();
    }
    public void Write(BinaryWriter w)
    {
        w.Write(is_Null);
        w.Write(_ulica);
        w.Write(_numerDomu);
        w.Write(_miasto);
        w.Write(_kodPocztowy);
        w.Write(_kraj);
    }
}