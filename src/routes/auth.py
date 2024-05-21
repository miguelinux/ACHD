from flask import Blueprint, render_template, request, redirect, session
from models.tables_db import Usuarios
from extensions import db
from functions import get_hex_digest
from functions import admin, docente, jefe_de_carrera
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@auth_bp.route("/login", methods=["POST"])
def login():
    form = request.form
    user = form["email"]
    pssw = get_hex_digest(form["password"])
    user = Usuarios.query.filter_by(email=user, password=pssw).first()
    if user is None:
        return render_template("index.html", mensaje="Usuario y/o contraseña incorrectos")

    session["user"] = {
        "userid": user.id,
        "name": user.nombre,
        "carrera": user.carrera,
    }

    if user.user_type == admin:
        return redirect("/homeDocente")
    if user.user_type == docente:
        return redirect("/homeDocente")
    if user.user_type == jefe_de_carrera:
        return redirect("/jefeCarrera")

    return redirect("/")

@auth_bp.route("/check", methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    
    usuario = Usuarios.query.filter_by(email=email).first()
    if usuario is None:
        return render_template("index.html", mensaje="El usuario no se encuentra")

    session["user"] = {
        "userid": usuario.id,
        "name": usuario.nombre,
        "carrera": usuario.carrera,
    }
    
    if usuario.first_login:
        return redirect("/firstlogin")
    if usuario.user_type == admin:
        return redirect("/admin")
    if usuario.user_type == docente:
        return redirect("/homeDocente")
    if usuario.user_type == jefe_de_carrera:
        return redirect("/jefeCarrera")
       
    return redirect("/")