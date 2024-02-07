# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import secrets
import string
from configparser import ConfigParser
from datetime import datetime
from datetime import timedelta

from flask import Flask
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask_orator import Orator

config = ConfigParser()
config.read("config.ini")


DB_HOST = config.get("DB", "DB_HOST")
DB_PASSWORD = config.get("DB", "DB_PASSWORD")
DB_DB = config.get("DB", "DB_DB")
DB_USER = config.get("DB", "DB_USER")

app = Flask(__name__)

DATABASES = {
    "default": "mysql",
    "mysql": {
        "driver": "mysql",
        "host": DB_HOST,
        "database": DB_DB,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "prefix": "",
        "log_queries": True,
    },
}


app.config["ORATOR_DATABASES"] = DATABASES
db = Orator(app)


def get_hex_digest(cadena):
    sha256 = hashlib.sha256()
    sha256.update(cadena.encode("utf-8"))
    hexdigest = sha256.hexdigest()

    return hexdigest


def get_session_random_id():
    caracteres = string.ascii_letters + string.digits
    randomString = "".join(secrets.choice(caracteres) for _ in range(64))

    return randomString


def verificar_sesion(cookies):
    try:
        sesion = (
            db.table("sesiones").where("sessionID", cookies["sessionID"]).get().first()
        )
        if sesion is None:
            return False
        if not sesion.active:
            return False
        if sesion.expires < datetime.now() - timedelta(hours=6):
            db.table("sesiones").where("sessionID", cookies["sessionID"]).update(
                active=False
            )
            return False
        return True
    except:
        return False


@app.route("/img/<filename>", methods=["GET"])
def route_img_files(filename):
    return send_from_directory("templates/img", path=filename)


@app.route("/css/<filename>")
def route_js_files(filename):
    return send_from_directory("templates/css", path=filename)


@app.route("/js/<filename>")
def route_css_files(filename):
    return send_from_directory("templates/js", path=filename)


@app.route("/")
def principal():
    if verificar_sesion(request.cookies):
        return make_response(redirect("/dashboard"))
    return render_template("index.html")



@app.route("/logout")
def logout():
    r = make_response(redirect("/"))
    r.set_cookie("sessionID", "")
    return r


@app.route("/login", methods=["POST"])
def login():
    try:
        form = request.form
    except Exception as e:
        return "NO SE PUDO INICIAR SESIÓN", str(e)
    print(str(form))
    user = form["email"]
    pssw = form["password"]

    user = (
        db.table("usersPrueba")
        .where("email", user)
        .where("password", get_hex_digest(pssw))
        .get()
        .first()
    )

    if user is None:
        return render_template(
            "index.html", mensaje="Usuario y/o contraseña incorrectos"
        )

    while True:
        sessionID = get_session_random_id()
        sesion = db.table("sesiones").where("sessionID", sessionID).get().first()
        if sesion is None:
            break

    # A CONSIDERACIÓN
    db.table("sesiones").insert(
        {
            "userID": user.id,
            "active": True,
            "created_at": datetime.now() - timedelta(hours=6),
            "updated_at": datetime.now() - timedelta(hours=6),
            "expires": datetime.now() + timedelta(hours=1),
            "sessionID": sessionID,
        }
    )
    r = make_response(redirect("/dashboard"))
    r.set_cookie("sessionID", sessionID)
    return r


@app.route("/dashboard")
def dashboard():
    cookies = request.cookies
    if not verificar_sesion(cookies):
        return make_response(redirect("/"))
    sesion = db.table("sesiones").where("sessionID", cookies["sessionID"]).get().first()
    user = db.table("usersPrueba").where("id", sesion.userID).get().first()

    d = db.table("datos_ejemplo").get()

    return render_template("dashboard.html", user=user, sesion=sesion, d_x=d)


@app.route("/homeDocente")
def home_docente():
    cookies = request.cookies
    if not verificar_sesion(cookies):
        return make_response(redirect("/"))
    sesion = db.table("sesiones").where("sessionID", cookies["sessionID"]).get().first()
    user = db.table("usersPrueba").where("id", sesion.userID).get().first()
    return render_template("homeDocente.html", user=user, sesion=sesion)
