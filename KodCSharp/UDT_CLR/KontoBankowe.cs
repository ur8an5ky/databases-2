using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.IO;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzKontoBankowe")]
public struct KontoBankowe : INullable, IBinarySerialize
{
    private bool is_Null;
    private string _numerKonta;
    private float _saldo;
    private string _waluta;
    //private Klient _wlasciciel;
    public bool IsNull
    {
        get
        { return (is_Null); }
    }
    public static KontoBankowe Null
    {
        get
        {
            KontoBankowe kb = new KontoBankowe();
            kb.is_Null = true;
            return kb;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            StringBuilder builder = new StringBuilder();
            builder.Append("Numer Konta: ");
            builder.Append(_numerKonta);
            builder.Append("; Saldo: ");
            builder.Append(_saldo);
            builder.Append(" ");
            builder.Append(_waluta);
            return builder.ToString();
        }
    }
    [SqlMethod(OnNullCall = false)]
    public static KontoBankowe Parse(SqlString s)
    {
        if (s.IsNull)
            return Null;
        KontoBankowe kb = new KontoBankowe();
        string[] xy = s.Value.Split(",".ToCharArray());
        kb.NumerKonta = xy[0];

        string saldoZWaluta = xy[1].TrimStart();
        int pierwszaSpacja = saldoZWaluta.IndexOf(' ');
        kb.Saldo = float.Parse(saldoZWaluta.Substring(0, pierwszaSpacja));
        kb.Waluta = saldoZWaluta.Substring(pierwszaSpacja + 1);

        if (!kb.SprawdzKontoBankowe())
            throw new ArgumentException("Nieprawid³owe konto bankowe.");
        return kb;
    }
    public string NumerKonta
    {
        get
        { return this._numerKonta; }
        set
        {
            string temp = _numerKonta;
            _numerKonta = value;
            if (!SprawdzKontoBankowe())
            {
                _numerKonta = temp; throw new ArgumentException("Z³y numer konta.");
            }
        }
    }
    public float Saldo
    {
        get
        { return this._saldo; }
        set
        {
            float temp = _saldo;
            _saldo = value;
            if (!SprawdzKontoBankowe())
            {
                _saldo = temp;
                throw new ArgumentException("Bledne saldo.");
            }
        }
    }
    public string Waluta
    {
        get
        { return this._waluta; }
        set
        {
            string temp = _waluta;
            _waluta = value;
            if (!SprawdzKontoBankowe())
            {
                _waluta = temp; throw new ArgumentException("Z³a waluta.");
            }
        }
    }
    //public Klient Wlasciciel
    //{
    //    get
    //    { return this._numerMieszkania; }
    //    set
    //    {
    //        Int32 temp = _numerMieszkania;
    //        _numerMieszkania = value;
    //        if (!SprawdzKontoBankowe())
    //        {
    //            _numerMieszkania = temp;
    //            throw new ArgumentException("Z³a wspó³rzêdna X.");
    //        }
    //    }
    //}
    private bool SprawdzKontoBankowe()
    {
        if ((!string.IsNullOrEmpty(_numerKonta) && _numerKonta.Length == 26) && (!string.IsNullOrEmpty(_waluta)))
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
        _numerKonta = r.ReadString();
        _saldo = r.ReadSingle();
        _waluta = r.ReadString();
    }
    public void Write(BinaryWriter w)
    {
        w.Write(is_Null);
        w.Write(_numerKonta);
        w.Write(_saldo);
        w.Write(_waluta);
    }
}