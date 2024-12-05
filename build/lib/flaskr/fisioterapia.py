from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('fisio', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    #recupero pazienti assegnati al fisioterapista loggato
    pazienti = db.execute(
        'SELECT p.ID_paziente, p.Data_di_nascita, p.genere, p.motivo_ visita, u.username '
        'FROM Paziente p '
        'JOIN user u ON p.ID_utente = u.id '
        'WHERE p.ID_FIsio = ? '
        'ORDER BY p.ID_pazienten DESC ',
        (g.user['id'],)
    ).fetchall()
    return render_template('fisioterapia/index.html', pazienti=pazienti)

@bp.route('/create_paziente', methods=('GET', 'POST'))
@login_required
def create_paziente():
    if request.method == 'POST' :
        username = request.form['username']
        data_nascita = request.form['data_nascita']
        genere = request.form['genere']
        motivo_visita = request.form['motivo_visita']
        error = None

        if not username:
            error = 'Il nome utente è obbligatorio'
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
            #verifica se utente esiste
            user = db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
            ).fetchone()

        if user is None:
            flash(f"Utente '{username}' non trovato")
        else:
            db.execute(
                'INSERT INTO Paziente (ID_utente, Data_di_nascita, genere, motivo_visita, ID_FIsio)'
                'VALUES (?, ?, ?, ?, ?)',
                (user['id'], data_nascita, genere, motivo_visita, g.user['id'])
            )
            db.commit()
            return redirect(url_for('fisioterapista.index'))
    return render_template('fisioterapista/create_paziente.html')

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
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE Paziente SET Data_di_nascita = ?, genere = ?, motivo_visita = ?'
                ' WHERE ID_paziente = ?',
                (data_nascita, genere, motivo_visita, id)
            )
            db.commit()
            return redirect(url_for('fisioterapia.index'))
    return render_template('fisioterapia/update_paziente.html', paziente=paziente)

@bp.route('/<int:id>/delete_paziente', methods=('POST',))
@login_required
def delete_paziente(id):
    get_paziente(id) #verifico che paziente esista e utente sia autorizzato
    db = get_db()
    db.execute('DELETE FROM Paziente WHERE ID_paziente = ?', (id))
    db.commit()
    flash(f"Paziente con ID {id} eliminato con successo")
    return redirect(url_for('fisioterapia.index'))