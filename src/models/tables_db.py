from extensions import db
from sqlalchemy.dialects.mysql import INTEGER, CHAR, VARCHAR, BOOLEAN, JSON
from sqlalchemy.orm import relationship

class Usuarios(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(CHAR(50), unique=True, nullable=False)
    password = db.Column(CHAR(65), nullable=False)
    user_type = db.Column(INTEGER(3), nullable=False)
    first_login = db.Column(BOOLEAN, nullable=False)
    nombre = db.Column(VARCHAR(50), nullable=False)
    apellido_pat = db.Column(VARCHAR(50), nullable=False)
    apellido_mat = db.Column(VARCHAR(50), nullable=False)
    habilitado = db.Column(BOOLEAN, nullable=False)
    
    disponibilidades = relationship("Disponibilidades", backref="usuario", cascade="all, delete-orphan", single_parent=True)
    docente_carreras = relationship("DocenteCarreras", backref="usuario", cascade="all, delete-orphan", single_parent=True)

    
class DocenteCarreras(db.Model):
    __tablename__ = 'docente_carrera'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carrera.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    

class Disponibilidades(db.Model):
    __tablename__ = 'disponibilidad'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    horas = db.Column(JSON)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    ciclo_id = db.Column(db.Integer, db.ForeignKey('ciclo.id'))    
    
class Carreras(db.Model):
    __tablename__ = 'carrera'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(VARCHAR(30), nullable=False)
    plan_de_estudio = db.Column(VARCHAR(15), nullable=False)
    
    materias_carrera = relationship("MateriasCarreras", backref="carrera", cascade="all, delete-orphan", single_parent=True)
    docente_carreras = relationship("DocenteCarreras", backref="carrera", cascade="all, delete-orphan", single_parent=True)
    grupo = relationship("Grupo", backref="carrera", cascade="all, delete-orphan", single_parent=True)

class Materias(db.Model):
    __tablename__ = 'materia'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clave = db.Column(CHAR(20), nullable=False)
    nombre = db.Column(VARCHAR(60), nullable=False)
    semestre = db.Column(INTEGER(3), nullable=False)
    horas_practica = db.Column(INTEGER(2), nullable=False)
    horas_teoria = db.Column(INTEGER(2), nullable=False)
    creditos = db.Column(INTEGER(2), nullable=False)
    
    materias_carrera = relationship("MateriasCarreras", backref="materia", cascade="all, delete-orphan", single_parent=True)


class MateriasCarreras(db.Model):
    __tablename__ = 'materias_carrera'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carrera.id'))
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))
    
class Aulas(db.Model):
    __tablename__ = 'aula'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(CHAR(10), nullable=False)
    edificio = db.Column(VARCHAR(20), nullable=False)

class Asignaciones(db.Model):
    __tablename__ = 'asignacion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    horario = db.Column(JSON)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo_semestre.id'))
    carrera_id = db.Column(db.Integer, db.ForeignKey('carrera.id'))
    ciclo_id = db.Column(db.Integer, db.ForeignKey('ciclo.id'))
    

class Ciclos(db.Model):
    __tablename__ = 'ciclo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    anio = db.Column(db.Integer, nullable=False)
    estacion = db.Column(CHAR(2), nullable=False)
    actual = db.Column(BOOLEAN, nullable=False)
    
    disponibilidades = relationship("Disponibilidades", backref="ciclo", cascade="all, delete-orphan", single_parent=True)
    asignaciones = relationship("Asignaciones", backref="ciclo", cascade="all, delete-orphan", single_parent=True)
    Grupo = relationship("Grupo", backref="ciclo", cascade="all, delete-orphan", single_parent=True)
    
    
class Grupo(db.Model):
    __tablename__ = 'grupo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    identificador = db.Column(db.String(5), nullable=False)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carrera.id'))
    ciclo_id = db.Column(db.Integer, db.ForeignKey('ciclo.id'))
    
    grupo_semestres = relationship("GrupoSemestre", backref="grupo", cascade="all, delete-orphan", single_parent=True)

    
class GrupoSemestre(db.Model):
    __tablename__ = 'grupo_semestre'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    semestre = db.Column(db.Integer, nullable=False)
    
    asignaciones = relationship("Asignaciones", backref="grupo_semestre", cascade="all, delete-orphan", single_parent=True)
    