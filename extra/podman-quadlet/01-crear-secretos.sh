#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Ejecutar este script para guardar las claves en podman

# crea_secreto nombre_de_env nombre_de_podman
crea_secreto()
{
    local env_name=$1
    local podman_name=$2
    if [ -n "${env_name}" ]
    then
        if podman secret exists ${podman_name}
        then
            podman secret rm ${podman_name}
        fi
        printf "${env_name}" | podman secret create ${podman_name} -
    fi
}

if [ -f .env ]
then
    source .env
else
    echo "No se encontro el archivo \".env\""
    exit 1
fi

crea_secreto "$MYSQL_ROOT_PASSWORD" achd-mrp
crea_secreto "$MYSQL_DATABASE" achd-md
crea_secreto "$MYSQL_USER" achd-mu
crea_secreto "$MYSQL_PASSWORD" achd-mp
