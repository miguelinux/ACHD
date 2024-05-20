from flask import Blueprint, render_template, redirect, request
from functions import verificate_session
from models.tables_db import Usuarios, Materias, Aulas

docente_bp = Blueprint('docente', __name__)

@docente_bp.route("/homeDocente")
def home_docente():
    user = verificate_session()
    if user:
        username = user["username"]
        return render_template("homeDocente.html", user=username)
    return redirect("/")

@docente_bp.route("/horario")
def horario():
    user = verificate_session()
    if user:
        user_id = user["userid"]
        usuario = Usuarios.query.filter_by(id=user_id).first()
        disponibilidad = usuario.disponibilidad
        return render_template("horario.html", user=user, disponibilidad=disponibilidad)
    return redirect("/")

@docente_bp.route("/horarioJ")
def horarioJefe():
    user = verificate_session()
    if user:
        try:
            user_id = request.args["userid"]
            if not user_id or user_id == "None":
                return "NO HA SELECCIONADO NINGÚN DOCENTE"
        except KeyError:
            return "NO HA SELECCIONADO NINGÚN DOCENTE"

        usuario = Usuarios.query.filter_by(id=user_id).first()
        try:
            disponibilidad = usuario.disponibilidad
        except AttributeError:
            return "EL HORARIO AÚN NO HA SIDO CARGADO POR EL DOCENTE"
        if not disponibilidad:
            return "EL HORARIO AÚN NO HA SIDO CARGADO POR EL DOCENTE"

        return render_template("horarioJ.html", user=user, disponibilidad=disponibilidad)
    return redirect("/")


@docente_bp.route("/mi-horario")
def clases():
    user = verificate_session()
    if user:
        user_name = user["username"]
        user_id = user["username"]
        usuario = Usuarios.query.filter_by(id=user_id).first()
        materia = Materias.query.all()
        aula = Aulas.query.all()
        return render_template("clases.html", user=user_name, materias = materia, aulas=aula)
    return redirect("/")