import sqlite3
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'

#BASE DE DONNEE#

# Connexion à la base de données SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Exécution du fichier schema.sql
with open('schema.sql', 'r') as file:
    schema_sql = file.read()
    cursor.executescript(schema_sql)

# Commit des changements et fermeture de la connexion
conn.commit()
conn.close()


#ROUTES#


@app.route('/')
def index():
    # Redirige vers l'URL '/login'
    return redirect(url_for('login'))

def valid_login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = valid_login
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return render_template('home.html')
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error, form=form)

@app.route('/home')
def home():
    return render_template('home.html')

#LOGIN FORM#
