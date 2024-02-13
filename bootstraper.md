# Bootstrap para Proyecto Asistente para la Creación de Horarios para Docentes

Este archivo contiene las instrucciones para configurar el entorno de desarrollo y la base de datos del proyecto Asistente para la Creación de Horarios para Docentes.

- Requisitos previos -
  * Python 3.8
  * Git
  * Pip


- Configuración del entorno -
  * Clona el repositorio de GitHub
  * Accede al directorio del proyecto
  * Instala las bibliotecas necesarias utilizando pip y el archivo requirements.txt:
    - pip install -r requirements.txt

- Creación de la base de datos -
  * Asegúrate de tener instalado un servidor de base de datos MySQL

  * Accede al terminal o línea de comandos MySQL y ejecuta la creación de tablas. La descripción de las tablas está en docs/tablas.txt

- Asegurate de modificar la configuración de la conexión a la base de datos -
 * En el archivo src\app.py, modifica la sección la constante "DATABASES" con la configuración de tu servidor de base de datos

- Ejecución del Proyecto -
  Para ejecutar el proyecto, ejecuta:
  * python
  * from app import app
  * app.run()
