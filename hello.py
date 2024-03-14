import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
app.config['DATABASE'] = 'database.db'

# Fonction pour obtenir une connexion SQLite
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

# Fonction pour fermer la connexion SQLite à la fin de la requête
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Connexion à la base de données SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
table_exists = cursor.fetchone()

# Exécution du fichier schema.sql
if not table_exists:
    with open('schema.sql', 'r') as file:
        schema_sql = file.read()
        cursor.executescript(schema_sql)
        conn.commit()

# Fonction pour vérifier si l'utilisateur existe déjà dans la base de données
def user_exists(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE username=?", (username,))
    return cursor.fetchone() is not None

#ROUTES#

@app.route('/')
def index():
    # Redirige vers l'URL '/login'
    return redirect(url_for('login'))

def validate_login(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validate_login(username, password)
        if user:
            flash('Connexion réussie pour {}'.format(username))
            return redirect(url_for('home'))
        else:
            error = 'Nom d\'utilisateur ou mot de passe incorrect'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if user_exists(username):
            flash('Ce nom d\'utilisateur est déjà utilisé. Veuillez en choisir un autre.')
        else:
            # Ajouter l'utilisateur à la base de données
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            flash('Inscription réussie ! Vous pouvez maintenant vous connecter.')
            return redirect('/login')
            
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')
