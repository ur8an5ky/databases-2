from flask import Flask
import pyodbc

app = Flask(__name__)
app.config['SECRET_KEY'] = '2493b92811db16ce03a76959'
app.jinja_env.filters['zip'] = zip
app.jinja_env.filters['enumerate'] = enumerate
app.config['logged_in'] = False
app.config['logged_in_id'] = -1
app.config['login'] = ''
app.config['koszyk'] = [(False, 0), (False, 0), (False, 0), (False, 0)]

server = 'LAPTOP-OSQFQF1M\SQLEXPRESS'
database = 'UDT_CLR'
cnxn = pyodbc.connect(f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};Trusted_Connection=yes')
cursor = cnxn.cursor()

dll_path = "..\\UDT_CLR\\bin\\Debug\\UDT_CLR.dll"

from App import routes