import os
from flask import Flask

def create_app(test_config=None):
    # creo e cofiguro l'app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', #chiave di sicurezza predefinita
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'), #percorso per il file db
    )
    #se il test_config è None, prova a caricare la configurazione dell'istanza
    if test_config is None:
        #carica la configurazione dal file 'config.py' nella cartella nella cartella dell'istanza(se presente)
        app.config.from_pyfile('config.py', silent=True)
    else:
        #carica la configurazione di test, se fornita
        app.config.from_mapping(test_config)

    # assicura che la cartella dell'istanza esista, se non esiste la crea
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # adefinisce una rotta '/hello' che restituisce una stringa di prova
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    #ritorna l'istanza dell'applicazione Flask configurata
    from . import db
    db.init_app(app)
    #collego il blueprint fatto in auth.py all'app:
    from . import auth
    app.register_blueprint(auth.bp)

    from . import fisioterapia
    app.register_blueprint(fisioterapia.bp) #registro blueprint
    app.add_url_rule('/', endpoint='index') #collego endpoint principale / alla vista principale del blueprint

    return app