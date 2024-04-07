#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# run_container.sh <achd_repo_path>
#
# Script que ejecuta el un contanedor y pone el repositorio de ACHD en
# /home/achd dentro del contenedor para su desarrollo

VTOOL=$(command -v podman)
VIMAGE=localhost/achd
VREPO=/path/to/achd

if [ -f ${HOME}/.config/achd.conf ]
then
    source ${HOME}/.config/achd.conf
fi

if [ -z "${VTOOL}" ]
then
    VTOOL=$(command -v docker)
    if [ -z "${VTOOL}" ]
    then
        echo >&2 "No podman or docker found."
        exit 1
    fi
fi

while [ -n "${1}" ]
do
    case "$1" in
        -d|--debug)
            set -x
        ;;
        -e|--error)
            set -e
        ;;
        *)
            if [ -d ${1}/.git ]
            then
                VREPO=$(realpath $1)
            fi
        ;;
    esac
    shift
done

if [ ! -d "${VREPO}" ]
then
    echo >&2 "${VREPO}: Not found."
    exit 1
fi

${VTOOL} run --rm --interactive --tty --name achd \
    --volume ${VREPO}:/home/achd:Z  \
    --publish 5000:5000 \
    ${VIMAGE}
