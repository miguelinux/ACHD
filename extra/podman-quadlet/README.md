# Quadlet para MySQL

Copia los archivos de

* `mysql-achd.container`
* `mysql-achd.volume`

a `$HOME/.config/containers/systemd`, para usar un contenedor de MySQL
en podman (usando quadlets).

Después reinicia el servicio de usuario de system con:

* `systemctl --user daemon-reload`

e inicia el servicio con:

* `systemctl --user start mysql-achd`

<!-- vi: set spl=es spell: -->
