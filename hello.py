import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for, g, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
app.config['DATABASE'] = 'database.db'


# Fonction pour obtenir une connexion SQLite
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def execute_query(query, args=(), one=False):
    db = get_db()
    cursor = db.execute(query, args)
    result = cursor.fetchall()
    cursor.close()
    db.commit()
    return (result[0] if result else None) if one else result


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
    if user:
        user_data = {'id': user[0], 'username': user[1]}  # Exemple de transformation en dictionnaire
        return user_data
    else:
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validate_login(username, password)
        if user:
            session['user_id'] = user['id']  # Ajouter l'ID de l'utilisateur à la session
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


def get_current_user_id():
    user_id = session.get('user_id')
    return user_id

def get_user_by_id(user_id):
    query = "SELECT username FROM user WHERE id = ?"
    user = execute_query(query, (user_id,), one=True)
    return user

@app.route('/home', methods=['GET', 'POST'])
def home(): 
    user_id = get_current_user_id()
    current_user = get_user_by_id(user_id)

    if request.method == 'POST':
        content = request.form['content']
        if content.strip():
            query = "INSERT INTO notes (user_id, content) VALUES (?, ?)"
            execute_query(query, (user_id, content))
            flash('Note ajoutée avec succès !')
        else:
            flash('Le contenu de la note ne peut pas être vide.')

    # Récupérer les notes de l'utilisateur connecté
    user_notes = get_user_notes(user_id)

    return render_template('home.html', notes=user_notes, current_user=current_user)


# Fonction pour récupérer les notes de l'utilisateur actuel
def get_user_notes(user_id):
    query = "SELECT * FROM notes WHERE user_id=?"
    user_notes = execute_query(query, (user_id,))
    return user_notes


def get_other_users_notes(user_id):
    query = "SELECT user.username, notes.content FROM notes INNER JOIN user ON notes.user_id = user.id WHERE notes.user_id != ?"
    return execute_query(query, (user_id,))


@app.route('/delete_selected_notes', methods=['POST'])
def delete_selected_notes():
    if request.method == 'POST':
        selected_notes = request.form.getlist('selected_notes')
        if selected_notes:
            placeholders = ','.join(['?'] * len(selected_notes))
            query = "DELETE FROM notes WHERE id IN ({})".format(placeholders)
            execute_query(query, tuple(selected_notes))
            flash('Les notes sélectionnées ont été supprimées avec succès !')
        else:
            flash('Aucune note sélectionnée pour la suppression.')
    return redirect(url_for('home'))


@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if request.method == 'POST':
        delete_query = "DELETE FROM notes WHERE id = ?"
        execute_query(delete_query, (note_id,))
        flash('Note supprimée avec succès.')
    return redirect(url_for('home'))


@app.route('/add_note', methods=['POST'])
def add_note():
    if request.method == 'POST':
        content = request.form['content']
        user_id = get_current_user_id()
        if content:
            query = "INSERT INTO notes (user_id, content) VALUES (?, ?)"
            execute_query(query, (user_id, content))
            flash('Note ajoutée avec succès !')
        else:
            flash('Veuillez entrer du contenu pour la note.')
    return redirect(url_for('home'))
