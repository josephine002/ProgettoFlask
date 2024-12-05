from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('fisio', __name__)

@bp.route('/')
@login_required
def fisio_home():
    db = get_db()
    # recupero pazienti assegnati al fisioterapista loggato
    pazienti = db.execute(
        'SELECT p.ID_paziente, p.Data_di_nascita, p.genere, p.motivo_visita, u.username '
        'FROM Paziente p '
        'JOIN user u ON p.ID_utente = u.id '
        'WHERE p.ID_FIsio = ? '
        'ORDER BY p.ID_paziente DESC ',
        (g.user['id'],)
    ).fetchall()
    return render_template('fisioterapia/index.html', pazienti=pazienti)


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('fisio', __name__)

@bp.route('/create_paziente', methods=('GET', 'POST'))
@login_required
def create_paziente():
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        data_nascita = request.form['data_nascita']
        genere = request.form['genere']
        motivo_visita = request.form['motivo_visita']
        error = None

        if not nome:
            error = 'Il nome è obbligatorio'
        elif not cognome:
            error = 'Il cognome è obbligatorio'
        elif not data_nascita:
            error = 'La data di nascita è obbligatoria'
        elif not genere:
            error = 'Il genere è obbligatorio'
        elif not motivo_visita:
            error = 'Il motivo della visita è obbligatorio'

        if error is not None:
            flash(error)
        else:
            db = get_db()

            # Creazione dello username basato su nome e cognome
            username = f"{nome.lower()}.{cognome.lower()}"
            password = data_nascita.split("-")[0]  # Estrae l'anno di nascita

            # Verifica se l'username esiste già nella tabella user
            existing_user = db.execute(
                "SELECT 1 FROM user WHERE username = ?", (username,)
            ).fetchone()

            if existing_user:
                flash(f"Errore: l'username {username} è già registrato.")
                print(f"DEBUG: L'username {username} è già presente nel database.")
            else:
                try:
                    # Inserisce l'utente nella tabella `user`
                    db.execute(
                        "INSERT INTO user (username, password) VALUES (?, ?)",
                        (username, generate_password_hash(password))
                    )
                    user_id = db.execute(
                        "SELECT id FROM user WHERE username = ?", (username,)
                    ).fetchone()['id']

                    print(f"DEBUG: L'ID dell'utente appena creato è {user_id}")

                    # Inserisce il paziente nella tabella `Paziente`
                    db.execute(
                        "INSERT INTO Paziente (ID_utente, Data_di_nascita, genere, motivo_visita, ID_FIsio) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (user_id, data_nascita, genere, motivo_visita, g.user['id'])
                    )
                    db.commit()
                    flash(f"Paziente {nome} {cognome} creato con successo! Username: {username}, Password: {password}")
                    return redirect(url_for('fisio.index'))
                except db.IntegrityError as e:
                    print(f"DEBUG: Errore di integrità {e}")
                    flash("Errore: utente o paziente già esistente.")

    return render_template('fisioterapia/create_paziente.html')



def get_paziente(id, check_author=True):
    paziente = get_db().execute(
        'SELECT p.ID_paziente, u.username, p.Data_di_nascita, p.genere, p.motivo_visita, p.ID_FIsio'
        ' FROM Paziente p JOIN user u ON p.ID_utente = u.id'
        ' WHERE p.ID_paziente = ?',
        (id,)
    ).fetchone()

    if paziente is None:
        abort(404, f"Paziente con ID {id} non trovato")

    if check_author and paziente['ID_FIsio'] != g.user['id']:
        abort(403)
    return paziente

@bp.route('/<int:id>/update_paziente', methods=('GET', 'POST'))
@login_required
def update_paziente(id):
    paziente = get_paziente(id)

    if request.method == 'POST':
        data_nascita = request.form['data_nascita']
        genere = request.form['genere']
        motivo_visita = request.form['motivo_visita']
        error = None

        if not data_nascita:
            error = 'La data di nascita è obbligatoria'

        if error is None:
            db = get_db()
            db.execute(
                'UPDATE Paziente SET Data_di_nascita = ?, genere = ?, motivo_visita = ?'
                ' WHERE ID_paziente = ?',
                (data_nascita, genere, motivo_visita, id)
            )
            db.commit()
            return redirect(url_for('fisio.fisio_home'))
    return render_template('fisioterapia/update_paziente.html', paziente=paziente)


@bp.route('/<int:id>/delete_paziente', methods=('POST',))
@login_required
def delete_paziente(id):
    paziente = get_paziente(id)  # Verifica che il paziente esista e che l'utente sia autorizzato
    db = get_db()
    db.execute('DELETE FROM Paziente WHERE ID_paziente = ?', (id,))
    db.commit()
    flash(f"Paziente con ID {id} eliminato con successo")
    return redirect(url_for('fisio.fisio_home'))


@bp.route('/<int:id>/assign_exercises', methods=('GET', 'POST'))
@login_required
def assign_exercises(id):
    paziente = get_paziente(id)
    db = get_db()
    packages = db.execute(
        'SELECT * FROM ExercisePackage'
    ).fetchall()

    if request.method == 'POST':
        selected_package = request.form['package']
        db.execute(
            'INSERT INTO PatientExercises (ID_patient, ID_package) VALUES (?, ?)',
            (id, selected_package)
        )
        db.commit()
        flash('Pacchetto di esercizi assegnato con successo!')
        return redirect(url_for('fisio.index'))

    return render_template('fisioterapia/assign_exercises.html', paziente=paziente, packages=packages)

