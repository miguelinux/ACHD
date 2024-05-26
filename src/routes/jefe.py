from flask import Blueprint, render_template, redirect, request, jsonify
from functions import verificate_session
from models.tables_db import Usuarios, Materias, Aulas, Asignaciones, Ciclos, Grupo
from models.tables_db import DocenteCarreras, MateriasCarreras, Disponibilidades, GrupoSemestre
from extensions import db
import json
from sqlalchemy.orm import joinedload
from functions import  docente

jefe_bp = Blueprint('jefe', __name__)

@jefe_bp.route("/jefeCarrera")
def jefe_carrera():
    user = verificate_session()
    if user:
        username = user["username"]
        return render_template("jefeCarrera.html", user=username)
    return redirect("/")


@jefe_bp.route("/jefeCarrera/docentes")
def docentes():
    user = verificate_session()
    if user:
        try:
            userid = request.args["userid"]
        except KeyError:
            userid = None
        username = user["username"]
        carrera = user["carrera"]
        
        docentes = (
            DocenteCarreras.query
            .join(Usuarios, DocenteCarreras.usuario_id == Usuarios.id)
            .filter(DocenteCarreras.carrera_id == carrera)
            .options(joinedload(DocenteCarreras.usuario))
            .order_by(Usuarios.nombre)
            .all()
        )
        return render_template("docentes.html", user=username, docentes=docentes, userid=userid)
    return redirect("/")


@jefe_bp.route("/jefeCarrera/semestre")
def semestre():
    user = verificate_session()
    if user:
        try:
            userid = request.args["userid"]
        except KeyError:
            userid = None
        username = user["username"]
        carrera = user["carrera"]
        
        semestre = (
            DocenteCarreras.query
            .join(Usuarios, DocenteCarreras.usuario_id == Usuarios.id)
            .filter(DocenteCarreras.carrera_id == carrera)
            .options(joinedload(DocenteCarreras.usuario))
            .order_by(Usuarios.nombre)
            .all()
        )
        return render_template("semestre.html", user=username, semestre=semestre, userid=userid)
    return redirect("/")

@jefe_bp.route("/jefeCarrera/materias")
def materias():
    user = verificate_session()
    if user:
        username = user["username"]
        carrera = user["carrera"]
        
        materias = (
            MateriasCarreras.query
            .join(Materias, MateriasCarreras.materia_id == Materias.id)
            .filter(MateriasCarreras.carrera_id == carrera)
            .options(joinedload(MateriasCarreras.materia))
            .order_by(Materias.semestre)
            .all()
        )
        return render_template("materias.html", user=username, materias=materias)
    return redirect("/")

@jefe_bp.route("/jefeCarrera/asignacion")
def asignacion():
    user = verificate_session()
    if user:
        username = user["username"]
        carrera = user["carrera"]
        ciclo = Ciclos.query.filter_by(actual=True).first()
        semestre = (
        DocenteCarreras.query
        .filter(DocenteCarreras.carrera_id == carrera)
        .outerjoin(Disponibilidades, DocenteCarreras.usuario_id == Disponibilidades.usuario_id)
        .filter(Disponibilidades.usuario_id != None,
                Disponibilidades.ciclo_id == ciclo.id)  # Filtra los semestre que no tienen disponibilidades
        .all()
        )
        asignatura= MateriasCarreras.query.filter_by(carrera_id=carrera)
        aula = Aulas.query.all()
        return render_template("asignacion.html", user=username, asignaturas=asignatura, semestre=semestre, aulas=aula)
    return redirect("/")


@jefe_bp.route("/setAsignacion", methods=["POST"])
def set_asignacion():
    user = verificate_session()
    if user:
        user_carrera = user["carrera"]
        asignacion_propuesta = request.json
        semestre = asignacion_propuesta.pop("semestre")
        turno = asignacion_propuesta.pop("turno")
        ciclo = Ciclos.query.filter_by(actual=True).first()
        asignacion = Asignaciones.query.filter_by(carrera_id=user_carrera, semestre=semestre, grupo=turno, ciclo_id=ciclo.id).first()

        if not asignacion:
            asignacion = Asignaciones(
                carrera_id=user_carrera,
                semestre=semestre,
                grupo=turno,
                ciclo_id=ciclo.id,
                horario=json.dumps(asignacion_propuesta.get("asignacion", {}))
            )
            horariov = None
            db.session.add(asignacion)
        else:
            horariov = json.loads(asignacion.horario)
            asignacion.horario = json.dumps(asignacion_propuesta.get("asignacion", {}))

        db.session.commit()
        horarion = json.loads(asignacion.horario)
        semestre = horarion.get("docente", [])
        cell_ids = horarion.get("cell_ids", [])

        semestre_actualizados = 0

        if horariov:
            actualizar = detectar_cambios(horarion, horariov)
            semestreold = actualizar.get("docente", [])
            cell_idsold = actualizar.get("cell_ids", [])

            for i, doc_id in enumerate(semestreold):
                if doc_id != '':
                    cell_id = int(cell_idsold[i])
                    if update_disp(doc_id, [cell_id], 1):
                        semestre_actualizados += 1

        for i, doc_id in enumerate(semestre):
            if doc_id != '':
                cell_id = int(cell_ids[i])
                if update_disp(doc_id, [cell_id], 3):
                    semestre_actualizados += 1

        if semestre_actualizados > 0:
            return jsonify({"success": True, "message": f"Disponibilidad actualizada para {semestre_actualizados} docente(s)"})
        else:
            return jsonify({"success": False, "message": "No se encontraron semestre con disponibilidad para actualizar"})

    return redirect("/")

def detectar_cambios(jsnew, jsold):
    cambios = {"docente": [], "cell_ids": []}
    for old_docente, new_docente, cell_id in zip(jsold["docente"], jsnew["docente"], jsnew["cell_ids"]):
        if old_docente != new_docente and old_docente != "":
            cambios["docente"].append(old_docente)
            cambios["cell_ids"].append(cell_id)
    return cambios

def update_disp(user_id, indices_to_update, value):
    ciclo = Ciclos.query.filter_by(actual=True).first()
    dispo= Disponibilidades.query.filter_by(usuario_id=user_id,ciclo_id=ciclo.id).first()
    
    if dispo:
        current_availability = json.loads(dispo.horas)["disponibilidad"]
        for idx in indices_to_update:
            current_availability[idx] = value

        result_dict = {"disponibilidad": current_availability}
        result_json = json.dumps(result_dict)

        dispo.horas = result_json
        db.session.commit()
        return True
    return False

@jefe_bp.route("/jefeCarrera/semestres")
def semestres():
    user = verificate_session()
    if user:
        username = user["username"]
        carrera = user["carrera"]
        semestre = DocenteCarreras.query.filter_by(carrera_id=carrera).all()
        asignaturas = MateriasCarreras.query.filter_by(carrera_id=carrera).all()
        aula = Aulas.query.all()
        return render_template("semestres.html", user=username, asignaturas=asignaturas, semestre=semestre, aulas=aula)
    return redirect("/")

@jefe_bp.route("/jefeCarrera/grupos")
def grupos():
    user = verificate_session()
    if user:
        username = user["username"]
        carrera = user["carrera"]
        ciclo = Ciclos.query.filter_by(actual=True).first()

        # Realizar join entre Grupo y GrupoSemestre
        resultados = db.session.query(Grupo, GrupoSemestre).outerjoin(GrupoSemestre, Grupo.id == GrupoSemestre.grupo_id)\
            .filter(Grupo.carrera_id == carrera, Grupo.ciclo_id == ciclo.id).all()
        
        # Agrupar los semestres por grupo
        grupos = {}
        for grupo, grupo_semestre in resultados:
            if grupo.id not in grupos:
                grupos[grupo.id] = {
                    'identificador': grupo.identificador,
                    'semestres': []
                }
            if grupo_semestre:
                grupos[grupo.id]['semestres'].append(grupo_semestre.semestre)

        for grupo_id in grupos:
            grupos[grupo_id]['semestres'].sort()

        return render_template("grupos.html", user=username, grupos=grupos)
    return redirect("/")


@jefe_bp.route("/crear_grupo", methods=["POST"])
def crear_carrera():
    """
    Metodo para agregar una carrera a la base de datos
    """
    user = verificate_session()
    if user:
        carrera = user["carrera"]
        ciclo=Ciclos.query.filter_by(actual=True).first()
        form = request.form
        identificador = form.get("identificador")
        
        nuevo_grupo = Grupo(
            identificador = identificador,
            carrera_id=carrera,
            ciclo_id=ciclo.id
        )
        db.session.add(nuevo_grupo)
        db.session.commit()
        return redirect("/jefeCarrera/grupos")
    else:
        return redirect("/")

def grupo_semestre(grupoid, semestre):
    # Verificar si el docente está asociado a la carrera en la base de datos
    return bool(GrupoSemestre.query.filter_by(grupo_id=grupoid, semestre=semestre).first())

@jefe_bp.route("/jefe/asignar_grupo_semestre/<int:grupoId>", methods=['GET'])
def grupos_semestre(grupoId):
    user = verificate_session()
    if user:
        username = user["username"]
        carrera = user["carrera"]
        ciclo=Ciclos.query.filter_by(actual=True).first()
        grupos = Grupo.query.filter_by(carrera_id=carrera,ciclo_id=ciclo.id).all()
        return render_template("grupo_semestre.html", user=username, grupos=grupos,
                    grupoId=grupoId,grupo_semestre=grupo_semestre)
    return redirect("/")


@jefe_bp.route("/guardar_gruposemestre", methods=['POST'])
def guardar_gruposemestre():
    user = verificate_session()
    if user:
        data = request.json
        grupoId = data["grupoId"]
        semestre_seleccionados = data["semestreSeleccionados"]
        semestre_deseleccionados = data["semestreDeseleccionados"]

        if semestre_deseleccionados:
            GrupoSemestre.query.filter(
                GrupoSemestre.grupo_id == grupoId,
                GrupoSemestre.semestre.in_(semestre_deseleccionados)
            ).delete(synchronize_session=False)

        if semestre_seleccionados:
            for semestre in semestre_seleccionados:
                if not GrupoSemestre.query.filter_by(grupo_id=grupoId, semestre=semestre).first():
                    nueva_relacion = GrupoSemestre(grupo_id=grupoId, semestre=semestre)
                    db.session.add(nueva_relacion)
        db.session.commit()

        return jsonify({"success": True})
    return redirect("/")


@jefe_bp.route("/delete/grupo", methods=["POST"])
def delete_grupo():
    """
    Método para borrar un grupo de la base de datos
    """
    user = verificate_session()
    if user:
        grupoid = request.form.get("id")
        grupo = Grupo.query.get(grupoid)
        if grupo:
            db.session.delete(grupo)
            db.session.commit()
        return redirect("/jefeCarrera/grupos")
    return redirect("/")