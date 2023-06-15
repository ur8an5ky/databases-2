using Microsoft.SqlServer.Server;
using System;
using System.Data.SqlTypes;
using System.Text;
using System.IO;

[Serializable]
[SqlUserDefinedType(Format.UserDefined,
IsByteOrdered = true, MaxByteSize = 8000, ValidationMethodName = "SprawdzNIP")]
public struct NIP : INullable, IBinarySerialize
{
    private bool is_Null;
    private string _nip;
    public bool IsNull
    {
        get
        { return (is_Null); }
    }
    public static NIP Null
    {
        get
        {
            NIP nip = new NIP();
            nip.is_Null = true;
            return nip;
        }
    }
    public override string ToString()
    {
        if (this.IsNull)
            return "NULL";
        else
        {
            StringBuilder builder = new StringBuilder();
            builder.Append(_nip.Insert(4, "-").Insert(7, "-").Insert(10, "-"));

            return builder.ToString();
        }
    }
    [SqlMethod(OnNullCall = false)]
    public static NIP Parse(SqlString s)
    {
        if (s.IsNull)
            return Null;

        NIP nip = new NIP();
        string xy = s.Value;
        nip.Nip = xy.Replace("-", "");

        if (!nip.SprawdzNIP())
            throw new ArgumentException("Nieprawid³owy Numer Identyfikacji Podatkowej.");
        return nip;
    }
    public string Nip
    {
        get
        { return this._nip; }
        set
        {
            string temp = _nip;
            _nip = value;
            if (!SprawdzNIP())
            {
                _nip = temp; throw new ArgumentException("Z³y Numer Identyfikacji Podatkowej.");
            }
        }
    }
    private bool SprawdzNIP()
    {
        if ((string.IsNullOrEmpty(_nip)) && (_nip.Length == 10))
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
        _nip = reader.ReadString();
    }
    public void Write(BinaryWriter writer)
    {
        // Serializacja danych
        writer.Write(is_Null);
        writer.Write(_nip);
    }
}