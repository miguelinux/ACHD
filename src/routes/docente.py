from flask import Blueprint, render_template, redirect, request
from functions import verificate_session
from models.tables_db import Usuarios, Materias, Disponibilidades,Asignaciones, Ciclos
import json


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
        ciclo=Ciclos.query.filter_by(actual=True).first()        
        d = Disponibilidades.query.filter_by(usuario_id=user_id,ciclo_id=ciclo.id).first()
        if not d.horas:
            d.horas = {'disponibilidad': [0]*90}
        disponibilidad = d.horas
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

        return render_template("horarioJ.html", user=user, disponibilidad=disponibilidad,usuario=usuario)
    return redirect("/")


@docente_bp.route("/mi-horario")
def clases():
    user = verificate_session()
    if user:
        user_name = user["username"]
        user_id = str(user["userid"])  # Convertimos el user_id a string para la comparación
        user_carrera = user["carrera"]
        ciclo = Ciclos.query.filter_by(actual=True).first()
        
        asignaciones = Asignaciones.query.filter_by(carrera=user_carrera, ciclo=ciclo.id).all()
        
        if asignaciones:
            materias_asignadas = set()  # Conjunto para almacenar las materias asignadas al docente

            for asignacion in asignaciones:
                horarios = json.loads(asignacion.horario)

                for i, docente_id in enumerate(horarios["docente"]):
                    if docente_id == user_id:
                        materia_id = horarios["materia"][i]
                        materia = Materias.query.get(materia_id)
                        if materia:
                            materias_asignadas.add(materia)  # Añadimos la materia asignada al conjunto

            return render_template("clases.html", user=user_name, materias=list(materias_asignadas))
        
    return redirect("/")