import os,sys
from utils.tools import uuidGen
from flask import *
from models.sqlmodel import db
from routes import defaults, crons, guis, api, csvrender
from submodules.logins import login_manager
from utils.yamlworks import readConf
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

if not os.path.exists(os.path.join(os.getcwd(),'config.yaml')):
    logging.critical("No config.yaml found.")
    sys.exit(1)
sqlinfo = readConf("config.yaml").get("database",{})

app = Flask(__name__)

if len(sqlinfo) == 0:
    logging.critical("No database information defined.")
    sys.exit(1)

def create_app(config=None):
    app = Flask(__name__)
    if config is not None:
        app.config.update(config)
    else:
        db_uri = (
            f"mysql+pymysql://{sqlinfo['username']}:{sqlinfo['password']}@"
            f"{sqlinfo['server']}:{sqlinfo['port']}/{sqlinfo['dbname']}"
        )
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SECRET_KEY'] = uuidGen()
    app.register_blueprint(defaults)
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(guis, url_prefix="/gui")
    app.register_blueprint(crons, url_prefix="/cron")
    app.register_blueprint(csvrender, url_prefix="/geofeed")
    db.init_app(app) # Create a new instance. db has been defined in sqlmodel.py
    login_manager.init_app(app)

    @app.errorhandler(404)
    def not_found(error):
        logging.warning("404 path: %s", request.path)
        return jsonify({
            "status": False,
            "message": "Requested resource not found."
        }), 404

    @app.errorhandler(Exception)
    def handle_exception(error):
        if isinstance(error, HTTPException):
            return error

        logger.error("Unhandled exception: %s", error, exc_info=True)

        return jsonify({
            "status": False,
            "message": "System cannot handle your request."
        }), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run()