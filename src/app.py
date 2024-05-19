# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import json
from configparser import ConfigParser
from datetime import timedelta

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session

from datetime import timedelta
from extensions import db
from models.tables_db import Usuarios, Materias, Aulas, Ciclos,Asignaciones, Carreras


app = Flask(__name__)

config = ConfigParser()
config.read(".env")  # EN ESTE APARTADO TOMARA LOS VALORES DE ENTORNO OBTENIDOS EN .env
app.secret_key = config.get("SCT", "SECRET_KY")
# para guardar las cookies es necesario una secret_key que se encuentra en .env
DB_HOST = config.get("DB", "DB_HOST")
DB_PASSWORD = config.get("DB", "DB_PASSWORD")
DB_DB = config.get("DB", "DB_DB")
DB_USER = config.get("DB", "DB_USER")

"""app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=15
)  # el tiempo de vida de la cookie
"""
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

docente = 3
jefe_de_carrera = 2
admin = 1


db.init_app(app)
with app.app_context():
    db.create_all()


def get_hex_digest(cadena):
    """
    Recibe un String.
    Regresa el hexadecimal de un Hash en SHA256.
    """
    sha256 = hashlib.sha256()
    sha256.update(cadena.encode("utf-8"))
    hexdigest = sha256.hexdigest()
    return hexdigest


def verificate_session():
    """verificate_session
    Returns:
        user: nombre del usuario en la cookie
        False: en caso de no tener encontrar la cookie
    """
    if "user" in session:
        user_id = session["user"]["userid"]
        username = session["user"]["name"]
        usercarrer = session["user"]["carrera"]
        return {"userid": user_id, "username": username, "carrera": usercarrer}
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
def index():
    """
    Si hay una sesión iniciada, redirecciona al dashboard.
    Si no hay una sesión iniciada, regresa el login.
    """

    user = verificate_session()
    if user:
        return redirect("dashboard")

    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404


@app.route("/logout")
def logout():
    """
    Borra las cookies del sitio en el navegador del usuario.
    """
    session.pop("user", None)
    return redirect("/")


@app.route("/login", methods=["POST"])
def login():
    """
    Método para iniciar sesión.
    Recibe el usuario y la contraseña de un form.
    Si coincide, inserta una sesión en la tabla de sesiones y regresa la
    cookie con el SessionID.
    """
    form = request.form
    user = form["email"]
    pssw = get_hex_digest(form["password"])
    user = Usuarios.query.filter_by(email=user, password=pssw).first()
    if user is None:
        return render_template(
            "index.html", mensaje="Usuario y/o contraseña incorrectos"
        )
    session["user"] = {
        "userid": user.id,
        "name": user.nombre,
        "carrera": user.carrera,
    }  #'user' hace referencia a la tabla de la base de datos

    if user.first_login:
        user.first_login = False
        db.session.commit()
        return redirect("/dashboard")
    if user.user_type == admin:
        return redirect("/homeDocente")
    if user.user_type == docente:
        return redirect("/homeDocente")
    if user.user_type == jefe_de_carrera:
        return redirect("/jefeCarrera")

    return redirect("/")

@app.route("/dashboard")
def dashboard():
    """
    Regresa la vista del dashboard.
    """
    user = verificate_session()
    if user:
        username = user["username"]
        return render_template("dashboard.html", user=username)
    return redirect("/")


@app.route("/change", methods=["POST", "GET"])
def change():
    user = verificate_session()
    if not user:
        return redirect("/")

    user_id = user["userid"]

    mensaje = None

    if request.method == "POST":
        current_password = request.form["password"]
        new_password = request.form["newpass"]
        confirm_password = request.form["conf_newpass"]

        if (
            current_password == ""  # nosec hardcoded_password_string
            or new_password == ""  # nosec hardcoded_password_string
            or confirm_password == ""  # nosec hardcoded_password_string
        ):
            mensaje = "Favor de llenar todos los campos"
            return jsonify({"success": False, "message": mensaje})
        else:
            usactual = Usuarios.query.filter_by(id=user_id).first()
            current_password = get_hex_digest(current_password)
            new_password = get_hex_digest(new_password)
            confirm_password = get_hex_digest(confirm_password)
            if current_password != usactual.password:
                mensaje = "La contraseña actual no coincide"
                return jsonify({"success": False, "message": mensaje})

            if new_password != confirm_password:
                mensaje = "La nueva contraseña no coincide"
                return jsonify({"success": False, "message": mensaje})

            if current_password == new_password:
                mensaje = "La nueva contraseña es la misma que la actual"
                return jsonify({"success": False, "message": mensaje})

            mensaje = (
                "La contraseña se cambió exitosamente. En 3 segundos serás redirigido"
            )
            usactual.password = new_password
            db.session.commit()

    return jsonify({"success": True, "message": mensaje})


@app.route("/getDisponibilidad")
def getDisponibilidad():
    user_id = request.args["id"]
    usuario = Usuarios.query.filter_by(id=user_id).first()
    disponibilidad = usuario.disponibilidad
    return jsonify(disponibilidad)


@app.route("/homeDocente")
def home_docente():
    """
    Regresa el panel de docente
    """
    user = verificate_session()
    if user:
        username = user["username"]
        return render_template("homeDocente.html", user=username)
    return redirect("/")


@app.route("/horario")
def horario():
    """
    Regresa el selector de horario
    """
    user = verificate_session()
    if user:
        user_id = user["userid"]
        usuario = Usuarios.query.filter_by(id=user_id).first()
        disponibilidad = usuario.disponibilidad

        return render_template("horario.html", user=user, disponibilidad=disponibilidad)
    return redirect("/")


@app.route("/horarioJ")
def horarioJefe():
    """
    Regresa el horario en solo lectura para
    la vista del jefe de carrera
    """
    user = verificate_session()
    if user:
        try:
            user_id = request.args["userid"]
            if user_id is None:
                return "NO HA SELECCIONADO NINGÚN DOCENTE"
            if user_id == "None":
                return "NO HA SELECCIONADO NINGÚN DOCENTE"
            print(f"userid: {user_id}")
        except KeyError:
            return "NO HA SELECCIONADO NINGÚN DOCENTE"

        usuario = Usuarios.query.filter_by(id=user_id).first()
        try:
            disponibilidad = usuario.disponibilidad
        except AttributeError:
            return "EL HORARIO AÚN NO HA SIDO CARGADO POR EL DOCENTE"
        if disponibilidad is None:
            return "EL HORARIO AÚN NO HA SIDO CARGADO POR EL DOCENTE"

        return render_template(
            "horarioJ.html", user=user, disponibilidad=disponibilidad
        )
    return redirect("/")


@app.route("/setDisponibilidad", methods=["POST"])
def set_disp():
    """
    Guarda la disponibilidad de un docente
    """
    user = verificate_session()
    if user:
        user_id = user["userid"]
        propuesta = request.json
        selected_ids = propuesta["selectedIDs"]
        selected_indices = [int(idx) for idx in selected_ids]
        availability_matrix = [0] * 90
        for idx in selected_indices:
            availability_matrix[idx] = 1

        result_dict = {"disponibilidad": availability_matrix}
        result_json = json.dumps(result_dict)

        usuario = Usuarios.query.filter_by(id=user_id).first()

        if usuario:
            usuario.disponibilidad = result_json
            db.session.commit()
            return jsonify(
                {"success": True, "message": "Disponibilidad actualizada correctamente"}
            )
    return redirect("/")

@app.route("/getDisponibilidad/<int:idDocente>", methods=["GET"])
def get_dispo(idDocente):
    """
    Función que permite al cliente obtener la disponibilidad del docente
    """
    user = verificate_session()
    if user:
        usuario = Usuarios.query.filter_by(id=idDocente).first()
        if usuario:
            disponibilidad = json.loads(usuario.disponibilidad)
            return jsonify({"success": True, "disponibilidad": disponibilidad})
        else:
            return jsonify({"success": False, "message": "Docente no encontrado"})
    else:
        return jsonify({"success": False, "message": "Usuario no autenticado"})


@app.route("/setAsignacion", methods=["POST"])
def set_asignacion():
    """
    Actualiza la asignación de horarios para un usuario y actualiza la disponibilidad del docente.
    """
    user = verificate_session()
    if user:
        user_carrera = user["carrera"]
        asignacion_propuesta = request.json

        semestre = asignacion_propuesta.pop("semestre")
        turno = asignacion_propuesta.pop("turno")

        ciclo = Ciclos.query.filter_by(actual=True).first()
        

        # Verificar si la asignación ya existe
        asignacion = Asignaciones.query.filter_by(carrera=user_carrera, semestre=semestre, turno=turno, ciclo=ciclo.id).first()

        # Si la asignación no existe, crear una nueva
        if not asignacion:
            asignacion = Asignaciones(
                carrera=user_carrera,
                semestre=semestre,
                turno=turno,
                ciclo=ciclo.id,
                horario=json.dumps(asignacion_propuesta.get("asignacion", {}))  # Convertir el dict a JSON
            )
            horariov = None
            db.session.add(asignacion)
        else:
            horariov = json.loads(asignacion.horario)
            asignacion.horario = json.dumps(asignacion_propuesta.get("asignacion", {}))
        
        
        # Commit a la base de datos para la asignación
        db.session.commit()
        horarion = json.loads(asignacion.horario)
        docentes = horarion.get("docente", [])
        cell_ids = horarion.get("cell_ids", [])
        
        docentes_actualizados=0
        
        if horariov:
            actualizar= detectar_cambios(horarion,horariov)
        
            docentesold = actualizar.get("docente", [])
            cell_idsold = actualizar.get("cell_ids", [])
        
            # Iterar sobre los docentes y sus IDs de celda correspondientes
            for i, doc_id in enumerate(docentesold):
                # Verificar si el docente tiene un ID válido (diferente de cadena vacía)
                if doc_id != '':
                    # Obtener el índice de la celda correspondiente a este docente
                    cell_id = int(cell_idsold[i])
                    
                    # Actualizar la disponibilidad del docente en el índice dado por cell_id
                    if update_disp(doc_id, [cell_id], 1):
                        # Incrementar el contador de docentes actualizados
                        docentes_actualizados += 1
        
        for i, doc_id in enumerate(docentes):
            # Verificar si el docente tiene un ID válido (diferente de cadena vacía)
            if doc_id != '':
                # Obtener el índice de la celda correspondiente a este docente
                cell_id = int(cell_ids[i])
                
                # Actualizar la disponibilidad del docente en el índice dado por cell_id
                if update_disp(doc_id, [cell_id], 3):
                    # Incrementar el contador de docentes actualizados
                    docentes_actualizados += 1

        # Verificar si se actualizó al menos un docente
        if docentes_actualizados > 0:
            return jsonify({"success": True, "message": f"Disponibilidad actualizada para {docentes_actualizados} docente(s)"})
        else:
            return jsonify({"success": False, "message": "No se encontraron docentes con disponibilidad para actualizar"})

    return redirect("/")

def detectar_cambios(jsnew, jsold):
    cambios = {"docente": [], "cell_ids": []}
    
    # Verificar si hay cambios en "docente"
    for old_docente, new_docente, cell_id in zip(jsold["docente"], jsnew["docente"], jsnew["cell_ids"]):
        if old_docente != new_docente and old_docente != "":
            cambios["docente"].append(old_docente)
            cambios["cell_ids"].append(cell_id)
    return cambios

def update_disp(user_id, indices_to_update, value):
    """
    Actualiza la disponibilidad de un docente dado su ID y los índices a actualizar.
    """
    usuario = Usuarios.query.filter_by(id=user_id).first()
    if usuario:
        current_availability = json.loads(usuario.disponibilidad)["disponibilidad"]
        for idx in indices_to_update:
            current_availability[idx] = value

        result_dict = {"disponibilidad": current_availability}
        result_json = json.dumps(result_dict)

        usuario.disponibilidad = result_json
        db.session.commit()
        return True
    return False
            
@app.route("/get_horario", methods=['GET'])
def get_horario():
    user = verificate_session()
    if user:
        carrera = user["carrera"]
        turno = request.args.get('turno')
        semestre = request.args.get('semestre')
        ciclo = Ciclos.query.filter_by(actual=True).first()
        asignacion = Asignaciones.query.filter_by(semestre=semestre, carrera=carrera, turno=turno, ciclo=ciclo.id).first()
        if asignacion:
            horarios = json.loads(asignacion.horario)
            return jsonify({"success": True, "horario": horarios})
        return jsonify({'error': 'Horario no encontrado'})
    return redirect("/")
        

@app.route("/jefeCarrera")
def jefe_carrera():
    """
    Vista del jefe de carrera
    """
    user = verificate_session()
    if user:
        username = user["username"]
        carrera = user["carrera"]
        d = Usuarios.query.filter_by(user_type=docente, carrera=carrera).all()
        a = Materias.query.filter_by(carrera=carrera).all()
        return render_template(
            "jefeCarrera.html", user=username, asignaturas=a, docentes=d
        )
    return redirect("/")


@app.route("/jefeCarrera/docentes")
def docentes():
    """
    Vista del jefe de carrera
    Menú de los docentes
    """
    user = verificate_session()
    if user:
        try:
            userid = request.args["userid"]
            print(f"userid: {userid}")
        except KeyError:
            userid = None
        username = user["username"]
        carrera = user["carrera"]
        d = (
            Usuarios.query.filter_by(user_type=docente, carrera=carrera)
            .order_by(Usuarios.apellido_pat)
            .all()
        )

        return render_template(
            "docentes.html", user=username, docentes=d, userid=userid
        )
    return redirect("/")


@app.route("/jefeCarrera/materias")
def materias():
    """
    Vista del jefe de carrera
    Menú de las materias
    """
    user = verificate_session()
    if user:
        username = user["username"]
        carrera = user["carrera"]
        d = Materias.query.filter_by(carrera=carrera).order_by(Materias.semestre).all()
        return render_template("materias.html", user=username, materias=d)
    return redirect("/")


@app.route("/jefeCarrera/docentes/agregar")
def docentes_agregar():
    """
    Vista del jefe de carrera
    Agregar un docente a la base de datos
    """
    user = verificate_session()
    if user:
        username = user["username"]
        return render_template("agregar_docente.html", user=username)
    return redirect("/")


@app.route("/jefeCarrera/asignacion")
def asignacion():
    """
    Vista de asignacion de materias

    """
    user = verificate_session()
    if user:
        username = user["username"]
        carrera = user["carrera"]
        d = Usuarios.query.filter_by(user_type=docente, carrera=carrera).all()
        a = Materias.query.filter_by(carrera=carrera).all()
        aula = Aulas.query.all()
        return render_template(
            "asignacion.html", user=username, asignaturas=a, docentes=d, aulas=aula
        )
    return redirect("/")

@app.route("/admin")
def admin():
    """
    Vista del administrador
    """
    user = verificate_session()
    if user:
        username = user["username"]
        return render_template(
            "admin.html", user=username
        )
    return redirect("/")

@app.route("/admin/usuarios")
def admin_docentes():
    """
    vista administrador con todos los docentes
    """
    user = verificate_session()
    if user:
        username = user["username"]
        usuarios = Usuarios.query.all()
        carrera = Carreras.query.all()
        
        return render_template(
            "admin_docentes.html", user=username, usuarios=usuarios,carreras=carrera
        )
    return redirect("/")


if __name__ == "__main__":
    app.run()
