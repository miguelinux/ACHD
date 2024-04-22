# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-License-Identifier: GPL-3.0-or-later


"""
Este programa permitira ingresar datos de prueba a la base de datos
"""

import pymysql

# Conexión a la base de datos MySQL
conn = pymysql.connect(
    host='tu_host',
    user='tu_usuario',
    password='tu_contraseña',
    database='tu_base_de_datos'
)
cursor = conn.cursor()

# Datos a insertar
datoscarrera =[
    ('ing prueba', 'ipru-0001')
]
'''
la contraseña: "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
hace referencia a la palabra "admin"
'''
datosusuario = [
    ('admin','root','prueb','admin@admin.com',
     '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
     '1','1','1'),
    ('Docente','prueb1','prueb','docente1@docente.com',
     '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
     '3','1','1'),
    ('Maestro','prueb2','pr','docente2@docente.com',
     '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
     '3','1','1')
]
datosmateria = [
    ('pru-0001', 'matprueb','1','1','1','2','1'),
    ('pru-0002', 'matpr2','2','1','1','2','1')
    
]
datosaula = [
    ('A1','principal')
    ('A2','principal')
]
# Consulta SQL de inserción
consultauser = "INSERT INTO usuario (nombre, apellido_pat, apellido_mat, email, password, user_type, first_login) VALUES (%s, %s, %s, %s, %s, %s, %s)"
consultcarrera = "INSERT INTO carrera (nombre, plan_de_estudio) VALUES (%s, %s)"
consultmateri = "INSERT INTO materia (clave, nombre, semestre, horas_practica, horas_teoria, creditos, carrera) VALUES (%s, %s, %s, %s, %s, %s, %s)"
consultaula = "INSERT INTO aula (nombre, edificio) VALUES (%s, %s)"

# Ejecutar la consulta para cada conjunto de datos

for dato in datoscarrera:
    cursor.execute(consultcarrera, dato)
for dato in datosusuario:
    cursor.execute(consultauser, dato)
for dato in datosmateria:
    cursor.execute(consultmateri, dato)
for dato in datosaula:
    cursor.execute(consultaula, dato)

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()
