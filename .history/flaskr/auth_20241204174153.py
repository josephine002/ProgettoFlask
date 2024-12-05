#importo i moduli necessari
import functools
from sqlite3 import IntegrityError
from werkzeug.security import generate_password_hash

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

#creo blueprint per funzioni autenticazione:
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
#funzione eseguita automaticamente prima di ogni richiesta grazie a comando qui sopra. 
def load_logged_in_user():
    user_id = session.get('user_id') #ottengo id da sessione
    #se utente autenticato, questa query recupera i dati utente dal db e li memorizza in g.user(globale in tutte le viste)
    if user_id is None:
        g.user = None #se non c'è id ,non c'è utente autenticato quindi None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone() #carico dati utente dal db
    print(f"DEBUG: Utente loggato? {g.user}")  # Debug temporaneo


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'fisioterapista'
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif not role:
            error = 'Role is required'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), role)
                )
                db.commit()
                return redirect(url_for('auth.login'))
            except db.IntegrityError:
                error = f"User {username} is already registered."

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:  # Controllo se l'utente è già loggato
        if g.user['role'] == 'fisioterapista':
            return redirect(url_for('fisio.index'))  # Home del fisioterapista
        elif g.user['role'] == 'paziente':
            return redirect(url_for('paziente.index'))  # Home del paziente

    if request.method == 'POST':
        # Estraggo nome e psw dal form via POST
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Controlla se l'utente esiste
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # Se l'utente non esiste
        if user is None:
            error = 'Incorrect username.'
        # Se invece utente esiste si confronta la psw inviata con quella memorizzata nel db
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # Se non ci sono errori, salva l'ID dell'utente nella sessione
        if error is None:
            session.clear()  # Pulisce qualsiasi sessione precedente
            session['user_id'] = user['id']  # Memorizza l'ID utente nella sessione
            g.user = user
            print(f"DEBUG: Login riuscito per {user['username']} con ruolo {user['role']}")

            # Controlla il ruolo e reindirizza
            if user['role'] == 'fisioterapista':
                return redirect(url_for('fisio.index'))  # Home del fisioterapista
            elif user['role'] == 'paziente':
                return redirect(url_for('paziente.index'))  # Home del paziente

        flash(error)  # Mostra l'errore

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear() #pulisce info sessione
    return redirect(url_for('index')) #reindirizzo a homepage

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view