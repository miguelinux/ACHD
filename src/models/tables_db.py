from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import TINYINT, JSON


db = SQLAlchemy()

class Carreras(db.Model):
    __tablename__ = 'carrera'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre =  db.Column(db.Text, nullable=False)
    plan_de_estudio = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f"<Carreras {self.id}>"

class Usuarios(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.Text, nullable=False)
    apellido_pat = db.Column(db.Text, nullable=False)
    apellido_mat = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    disponibilidad = db.Column(JSON, nullable=True, default=None)
    user_type = db.Column(db.Integer, nullable=False)
    first_login = db.Column(TINYINT(1), nullable=False)
    horas_semana = db.Column(db.Integer, nullable=True, default=None)
    carrera = db.Column(db.Integer, nullable=True, default=None)

    def __repr__(self):
        return f"<Usuarios {self.id}>"
    
class Materias(db.Model):
    __tablename__ ='materia'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clave = db.Column(db.Text, nullable=False)
    nombre = db.Column(db.Text, nullable=False)
    semestre = db.Column(db.Integer, nullable=False)
    horas_practica = db.column(db.Integer, nullable=False)
    horas_teoria = db.column(db.Integer, nullable=False)
    creditos = db.column(db.Integer, nullable=False)
    carrera = db.Column(db.Integer, nullable=True, default=None)

    def __repr__(self):
        return f"<Materias {self.id}>"

class Aulas(db.Model):
    __tablename__ = 'aula'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre =  db.Column(db.Text, nullable=False)
    edificio = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f"<Aulas {self.id}>"
    
class Asignaciones(db.Model):
    __tablename__='asignacion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    horario = db.Column(JSON, nullable=True, default=None)
    semestre = db.Column(db.Integer, nullable=False)
    carrera = db.Column(db.Integer, nullable=False)
    turno = db.Column(db.Text, nullable = False)
    ciclo = db.Column(db.Text, nullable = False)

    def __repr__(self):
        return f"<Asignaciones {self.id}>"
    
class Logg (db.Model):
    __tablename__='loggs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DATE, nullable=False)

    def __repr__(self):

        return f"<Logg {self.id}>"


