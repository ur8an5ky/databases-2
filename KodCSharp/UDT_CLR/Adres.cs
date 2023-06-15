using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.IO;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzAdres")]
public struct Adres : INullable, IBinarySerialize
{
    private bool is_Null;
    private string _ulica;
    private Int32 _numerDomu;
    private Int32 _numerMieszkania;
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
            StringBuilder builder = new StringBuilder();
            builder.Append("ul. ");
            builder.Append(_ulica);
            builder.Append(" ");
            builder.Append(_numerDomu);
            if (NumerMieszkania != -1)
            {
                builder.Append("/");
                builder.Append(_numerMieszkania);
            }
            builder.Append(",");
            builder.Append(_miasto);
            builder.Append(" ");
            builder.Append(_kodPocztowy);
            builder.Append(",");
            builder.Append(_kraj);
            return builder.ToString();
        }
    }
    [SqlMethod(OnNullCall = false)]
    public static Adres Parse(SqlString s)
    {
        if (s.IsNull)
            return Null;
        Adres ad = new Adres();
        string[] xy = s.Value.Split(",".ToCharArray());
        string ulicaOrazNumer = xy[0];
        int ostatniaSpacja = ulicaOrazNumer.LastIndexOf(' ');
        string numer = ulicaOrazNumer.Substring(ostatniaSpacja + 1);
        ad.Ulica = ulicaOrazNumer.Substring(0, ostatniaSpacja).TrimEnd();
        int domCzyMieszkanie = numer.IndexOf('/');
        if (domCzyMieszkanie != -1)
        {
            ad.NumerDomu = Int32.Parse(numer.Substring(0, domCzyMieszkanie));
            ad.NumerMieszkania = Int32.Parse(numer.Substring(domCzyMieszkanie + 1));
        }
        else
        {
            ad.NumerDomu = Int32.Parse(numer);
            ad.NumerMieszkania = -1;
        }

        string kodOrazMiasto = xy[1].TrimStart();
        int pierwszaSpacja = kodOrazMiasto.IndexOf(' ');
        ad.KodPocztowy = kodOrazMiasto.Substring(0, pierwszaSpacja);
        ad.Miasto = kodOrazMiasto.Substring(pierwszaSpacja + 1);

        ad.Kraj = xy[2].TrimStart();

        if (!ad.SprawdzAdres())
            throw new ArgumentException("Nieprawid³owy adres.");
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
            if (!SprawdzAdres())
            {
                _ulica = temp; throw new ArgumentException("Z³a nazwa ulicy.");
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
            if (!SprawdzAdres())
            {
                _numerDomu = temp;
                throw new ArgumentException("Z³a wspó³rzêdna X.");
            }
        }
    }
    public Int32 NumerMieszkania
    {
        get
        { return this._numerMieszkania; }
        set
        {
            Int32 temp = _numerMieszkania;
            _numerMieszkania = value;
            if (!SprawdzAdres())
            {
                _numerMieszkania = temp;
                throw new ArgumentException("Z³a wspó³rzêdna X.");
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
            if (!SprawdzAdres())
            {
                _kodPocztowy = temp; throw new ArgumentException("Z³y kod pocztowy.");
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
            if (!SprawdzAdres())
            {
                _miasto = temp; throw new ArgumentException("Z³a nazwa miasta.");
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
            if (!SprawdzAdres())
            {
                _kraj = temp; throw new ArgumentException("Z³a nazwa kraju.");
            }
        }
    }
    private bool SprawdzAdres()
    {
        if ((string.IsNullOrEmpty(_ulica)) && (_numerDomu > 0) && (_numerMieszkania == -1 || _numerMieszkania > 0)
                && (string.IsNullOrEmpty(_miasto)) && (string.IsNullOrEmpty(_kodPocztowy))
                && (string.IsNullOrEmpty(_kraj)))
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    public void Read(BinaryReader reader)
    {
        // Deserializacja danych
        is_Null = reader.ReadBoolean();
        _ulica = reader.ReadString();
        _numerDomu = reader.ReadInt32();
        _numerMieszkania = reader.ReadInt32();
        _miasto = reader.ReadString();
        _kodPocztowy = reader.ReadString();
        _kraj = reader.ReadString();
    }
    public void Write(BinaryWriter writer)
    {
        // Serializacja danych
        writer.Write(is_Null);
        writer.Write(_ulica);
        writer.Write(_numerDomu);
        writer.Write(_numerMieszkania);
        writer.Write(_miasto);
        writer.Write(_kodPocztowy);
        writer.Write(_kraj);
    }
}