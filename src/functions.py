import hashlib
import random
from flask import session

#variables globales
docente = 3
jefe_de_carrera = 2
admin = 1

def get_hex_digest(cadena):
    """
    Recibe un String.
    Regresa el hexadecimal de un Hash en SHA256.
    """
    sha256 = hashlib.sha256()
    sha256.update(cadena.encode("utf-8"))
    hexdigest = sha256.hexdigest()
    return hexdigest

def random_number():
    """
    Funcion para generar numeros randoms, para asignarlos de contraseña principal
    """
    number =0
    for _ in range(5):
        numero = random.randint(0, 100)
        number=numero+number
    return number


def verificate_session():
    """verificate_session
    Returns:
        user: nombre del usuario en la cookie
        False: en caso de no tener encontrar la cookie
    """
    if "user" in session:
        user_id = session["user"]["userid"]
        username = session["user"]["name"]
        nivel = session["user"]["nivel"]
        usercarrer = session["user"]["carrera"]
        return {"userid": user_id, "username": username, "carrera": usercarrer, "nivel": nivel}
    return False

