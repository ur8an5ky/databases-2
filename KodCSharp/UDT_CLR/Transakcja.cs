using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.IO;
using System.Globalization;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzTransakcje")]
public struct Transakcja: INullable, IBinarySerialize
{
    private bool is_Null;
    private float _kwota;
    private DateTime _dataTransakcji;
    public bool IsNull
    {
        get
        { return (is_Null); }
    }
    public static Transakcja Null
    {
        get
        {
            Transakcja tr = new Transakcja();
            tr.is_Null = true;
            return tr;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            return $"Zaplacono {_kwota} zl, {_dataTransakcji} r.";

        }
    }
    [SqlMethod(OnNullCall = false)]
    public static Transakcja Parse(SqlString s)
    {
        if (s.IsNull)
            throw new ArgumentNullException(nameof(s));

        string[] parts = s.Value.Split(';');

        if (parts.Length != 2)
            throw new ArgumentException("Nieprawid³owy format napisu. Oczekiwano: 'kwota;dataTransakcji'");

        Transakcja tr = new Transakcja();
        tr.Kwota = float.Parse(parts[0]);
        tr.DataTransakcji = DateTime.ParseExact(parts[1], "dd.MM.yyyy", CultureInfo.InvariantCulture);

        if (!tr.SprawdzTransakcje())
            throw new ArgumentException("Nieprawidlowa Transakcja.");
        return tr;
    }
    public float Kwota
    {
        get
        { return this._kwota; }
        set
        {
            float temp = _kwota;
            _kwota = value;
            if (_kwota <= 0.0)
            {
                _kwota = temp; throw new ArgumentException("Zla kwota.");
            }
        }
    }
    public DateTime DataTransakcji
    {
        get
        { return this._dataTransakcji; }
        set
        {
            DateTime temp = _dataTransakcji;
            _dataTransakcji = value;
            if (_dataTransakcji < new DateTime(2020, 1, 1))
            {
                _dataTransakcji = temp; throw new ArgumentException("Nieprawidlowa data transakcji.");
            }
        }
    }
    private bool SprawdzTransakcje()
    {
        if ((_dataTransakcji >= new DateTime(2020, 1, 1)) && (_kwota > 0.0))
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
        _dataTransakcji = DateTime.FromBinary(r.ReadInt64()); ;
        _kwota = r.ReadSingle();
    }
    public void Write(BinaryWriter w)
    {
        w.Write(is_Null);
        w.Write(_dataTransakcji.ToBinary());
        w.Write(_kwota);
    }
}