# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-License-Identifier: GPL-3.0-or-later

import hashlib
import string
import secrets
import json

from datetime import datetime
from datetime import timedelta

from flask import Flask, render_template, send_from_directory, request, make_response, redirect
from configparser import ConfigParser
from flask_orator import Orator


app=Flask(__name__)

config = ConfigParser()
config.read(".env")

DB_HOST = config.get("DB", "DB_HOST")
DB_PASSWORD = config.get("DB", "DB_PASSWORD")
DB_DB = config.get("DB", "DB_DB")
DB_USER = config.get("DB", "DB_USER")

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
    """
    Recibe un String.
    Regresa el hexadecimal de un Hash en SHA256.
    """
    sha256 = hashlib.sha256()
    sha256.update(cadena.encode("utf-8"))
    hexdigest = sha256.hexdigest()

    return hexdigest


def get_session_random_id():
    """
    Regresa 64 caracteres alfanuméricos aleatorios.
    Se utiliza para generar ID de sesión aleatorios.
    """
    caracteres = string.ascii_letters + string.digits
    random_string = "".join(secrets.choice(caracteres) for _ in range(64))

    return random_string


def verificar_sesion(cookies):
    """
    Recibe las cookies de la solicitud HTTPS.
    Verifica si hay una sesión asociada la SessionID encontrada en las cookies.
    Regresa True si la sesión es válida, está activa y no ha expirado.
    En caso contrario, regresa False.
    """
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
    except TypeError as e:
        print("Hubo un error al iniciar sesión", e)
        return False
    except Exception as e:
        print("ERROR AL INICIAR SESIÓN", e)
        return False
    

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


@app.route("/")
def principal():
    """
    Si hay una sesión iniciada, redirecciona al dashboard.
    Si no hay una sesión iniciada, regresa el login.
    """
    if verificar_sesion(request.cookies):
        return make_response(redirect("/dashboard"))
    return render_template("index.html")

@app.route("/logout")
def logout():
    """
    Borra las cookies del sitio en el navegador del usuario.
    """

    # FALTA HACER QUE ACTUALICE LA SESIÓN A INACTIVA EN LA BASE DE DATOS
    r = make_response(redirect("/"))
    r.set_cookie("sessionID", "")
    return r

@app.route("/login", methods=["POST"])
def login():
    """
    Método para iniciar sesión.
    Recibe el usuario y la contraseña de un form.
    Si coincide, inserta una sesión en la tabla de sesiones y regresa la
    cookie con el SessionID.
    """
    form = request.form

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
        session_id = get_session_random_id()
        sesion = db.table("sesiones").where("sessionID", session_id).get().first()
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
            "sessionID": session_id,
        }
    )
    r = make_response(redirect("/dashboard"))
    r.set_cookie("sessionID", session_id)
    return r

@app.route("/dashboard")
def dashboard():
    """
    Regresa la vista del dashboard.
    """
    cookies = request.cookies
    if not verificar_sesion(cookies):
        return make_response(redirect("/"))
    sesion = db.table("sesiones").where("sessionID", cookies["sessionID"]).get().first()
    user = db.table("usersPrueba").where("id", sesion.userID).get().first()


    return render_template("dashboard.html", user=user, sesion=sesion)



@app.route("/homeDocente")
def home_docente():
    """
    Regresa el panel de docente
    """
    cookies = request.cookies
    if not verificar_sesion(cookies):
        return make_response(redirect("/"))
    sesion = db.table("sesiones").where("sessionID", cookies["sessionID"]).get().first()
    user = db.table("usersPrueba").where("id", sesion.userID).get().first()
    return render_template("homeDocente.html", user=user, sesion=sesion)


@app.route("/horarioPrueba")
def horario_prueba():
    """
    Regresa el panel de docente
    """
    cookies = request.cookies
    if not verificar_sesion(cookies):
        return make_response(redirect("/"))
    sesion = db.table("sesiones").where("sessionID", cookies["sessionID"]).get().first()
    user = db.table("usersPrueba").where("id", sesion.userID).get().first()
    return render_template("Horario-prueba.html", user=user, sesion=sesion)

@app.route("/horario")
def horario():
    """
    Regresa el selector de horario
    """
    cookies = request.cookies
    if not verificar_sesion(cookies):
        return make_response(redirect("/"))
    sesion = db.table("sesiones").where("sessionID", cookies["sessionID"]).get().first()
    user = db.table("usersPrueba").where("id", sesion.userID).get().first()
    disponibilidad = user.disponibilidad
    return render_template("horario.html", user=user, sesion=sesion,disponibilidad=disponibilidad)

@app.route("/setDisponibilidad", methods=['POST'])
def set_disp():
    """
    Guarda la disponibilidad de un docente
    """
    cookies = request.cookies
    if not verificar_sesion(cookies):
        return make_response(redirect("/"))
    sesion = db.table("sesiones").where("sessionID", cookies["sessionID"]).get().first()
    user = db.table("usersPrueba").where("id", sesion.userID).get().first()
    propuesta = request.json
    selected_ids = propuesta['selectedIDs']
    selected_indices = [int(idx) for idx in selected_ids]
    availability_matrix = [0] * 90
    for idx in selected_indices:
        availability_matrix[idx] = 1
    result_dict = {"disponibilidad": availability_matrix}
    result_json = json.dumps(result_dict)

    resp = db.table('usersPrueba').where('user',user.user).update(disponibilidad=result_json)


    return str(resp)






if __name__=='__main__':
    app.run(debug=True, port=5000)