# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-License-Identifier: GPL-3.0-or-later
from configparser import ConfigParser
from flask import Flask
from flask import send_from_directory

from datetime import timedelta
from extensions import db

from routes import register_blueprints

app = Flask(__name__)

config = ConfigParser()
config.read(".env")  # EN ESTE APARTADO TOMARA LOS VALORES DE ENTORNO OBTENIDOS EN .env
app.secret_key = config.get("SCT", "SECRET_KY")
# para guardar las cookies es necesario una secret_key que se encuentra en .env
DB_HOST = config.get("DB", "DB_HOST")
DB_PASSWORD = config.get("DB", "DB_PASSWORD")
DB_DB = config.get("DB", "DB_DB")
DB_USER = config.get("DB", "DB_USER")

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=30
)  # el tiempo de vida de la cookie

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_DB}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# TODO: Hay que mejorar esto por favor
ETAPA = config.get("APP", "ETAPA")

if ETAPA == "desarrollo":
    app.config["DEBUG"] = True

SERVER_NAME = config.get("APP", "SERVER_NAME")
PORT = config.get("APP", "PORT")
app.config["SERVER_NAME"] = SERVER_NAME + ":" + PORT

db.init_app(app)
with app.app_context():
    db.create_all()

register_blueprints(app)

@app.route("/img/<filename>", methods=["GET"])
def route_img_files(filename):
    """
    Recibe la ruta de la imagen que pide.
    Regresa la imagen.
    """
    return send_from_directory("templates/img", path=filename)


@app.route("/css/<filename>")
def route_js_files(filename):
    """
    Recibe la ruta del CSS que se pide.
    Regresa el archivo CSS.
    """
    return send_from_directory("templates/css", path=filename)


@app.route("/js/<filename>")
def route_css_files(filename):
    """
    Recibe la ruta del JS que pide.
    Regresa el JS.
    """
    return send_from_directory("templates/js", path=filename)

if __name__ == "__main__":
    app.debug=True
    app.run()
