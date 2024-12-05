import sqlite3 
from datetime import datetime #per ottenere timestamp

import click #per creare comandi CLI
from flask import current_app, g #oggetti speciali flask

def get_db(): #verifica se esiste già connessione al db
    if 'db' not in g: #se non esiste crea nuova connessione
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], #percorso del db, letto dalla configurazione dell'app
            detect_types=sqlite3.PARSE_DECLTYPES #permette a SQLite di riconoscere dati come datetime
        )
        g.db.row_factory = sqlite3.Row #imposta row_factory per restituire righe accessibili per nomi colonne

    return g.db #ritorna connessione esistente(o appena creata)

def close_db(e=None): #recupera la connessione da g se esiste
    db = g.pop('db', None)

    if db is not None: #chiudo la conn, se presente.
        db.close()

def init_db(): #inizializzo database eseguendo comandi SQL dal file schema.sql
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app): #registra close e init xon l'app
    app.teardown_appcontext(close_db) #indica a flask di richiamare questa funzione durante pulizia dopo aver restituito risposta
    app.cli.add_command(init_db_command) #aggiunge nuovo comando che può esser chiamato con comando flask