from flask import Blueprint, render_template, g, redirect, url_for
from flaskr.db import get_db
from flaskr.auth import login_required

# Crea il blueprint per la sezione 'paziente'
bp = Blueprint('paziente', __name__, url_prefix='/paziente')

@bp.route('/')
@login_required
def paziente_home():
    # Verifica che l'utente loggato sia un paziente
    if g.user['role'] != 'paziente':
        return redirect(url_for('auth.login'))  # Se non è un paziente, lo rimandiamo al login

    # Esercizi disponibili
    esercizi = [
        {"nome": "Esercizio 1", "link": "http://esercizio1.com"},
        {"nome": "Esercizio 2", "link": "http://esercizio2.com"},
        {"nome": "Esercizio 3", "link": "http://esercizio3.com"},
        {"nome": "Esercizio 4", "link": "http://esercizio4.com"},
    ]
    return render_template('paziente/index.html', esercizi=esercizi)

# Aggiungi altre rotte per la gestione delle informazioni del paziente, se necessario
