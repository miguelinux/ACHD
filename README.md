Es necesario tener un entorno virtual para poder ejecutar este programa, de igual forma hay una lista de requerimientos, por lo que se debera usar el siguiente comando

pip install -r ./docs/requiriment.txt


delmismo modo es requerido una base de datos con una tabla, la cual se encuentra en /docs/ como tablaDB.txt

se cuentan con variables de entorno por lo que deberas hacer un archivo .env en raiz con dichas variables de entorno:
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = '' <- tu password
DB_DATABASE = 'prueba'
