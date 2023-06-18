using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.IO;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzProdukt")]
public struct Produkt : INullable, IBinarySerialize
{
    private bool is_Null;
    private string _producent;
    private string _model;
    private float _cena;
    private Int32 _dostepnosc;
    public bool IsNull
    {
        get
        { return (is_Null); }
    }
    public static Produkt Null
    {
        get
        {
            Produkt pr = new Produkt();
            pr.is_Null = true;
            return pr;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            return $"Producent: {_producent}, Model: {_model}, Cena: {_cena}, Dostêpnoœæ: {_dostepnosc}";
        }
    }
    [SqlMethod(OnNullCall = false)]
    public static Produkt Parse(SqlString s)
    {
        if (s.IsNull)
            throw new ArgumentNullException(nameof(s));

        string[] parts = s.Value.Split(';');

        if (parts.Length != 4)
            throw new ArgumentException("Nieprawid³owy format napisu. Oczekiwano: 'producent;model;cena;dostêpnoœæ'");

        Produkt produkt = new Produkt();
        produkt.Producent = parts[0];
        produkt.Model = parts[1];

        produkt.Cena = float.Parse(parts[2]);
        produkt.Dostepnosc = Int32.Parse(parts[3]);

        if (!produkt.SprawdzProdukt())
            throw new ArgumentException("Nieprawidlowe dane produktu.");
        return produkt;
    }
    public string Producent
    {
        get
        { return this._producent; }
        set
        {
            string temp = _producent;
            _producent = value;
            if (string.IsNullOrEmpty(_producent))
            {
                _producent = temp; throw new ArgumentException("Zly producent.");
            }
        }
    }
    public string Model
    {
        get
        { return this._model; }
        set
        {
            string temp = _model;
            _model = value;
            if (string.IsNullOrEmpty(_model))
            {
                _model = temp; throw new ArgumentException("Zly model.");
            }
        }
    }
    public float Cena
    {
        get
        { return this._cena; }
        set
        {
            float temp = _cena;
            _cena = value;
            if (_cena <= 0.0)
            {
                _cena = temp; throw new ArgumentException("Nieprawidlowa cena.");
            }
        }
    }
    public Int32 Dostepnosc
    {
        get
        { return this._dostepnosc; }
        set
        {
            Int32 temp = _dostepnosc;
            _dostepnosc = value;
            if (!(_dostepnosc > 0) && (_dostepnosc < 101))
            {
                _dostepnosc = temp; throw new ArgumentException("Nieprawidlowa dostepnosc.");
            }
        }
    }
    private bool SprawdzProdukt()
    {
        if ((!string.IsNullOrEmpty(_producent)) && (!string.IsNullOrEmpty(_model)) && (_cena > 0.0) && ((_dostepnosc > 0) && (_dostepnosc < 101)))
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
        _producent = r.ReadString();
        _model = r.ReadString();
        _cena = r.ReadSingle();
        _dostepnosc = r.ReadInt32();
    }
    public void Write(BinaryWriter w)
    {
        w.Write(is_Null);
        w.Write(_producent);
        w.Write(_model);
        w.Write(_cena);
        w.Write(_dostepnosc);
    }
}