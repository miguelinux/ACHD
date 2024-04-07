#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
#
# SPDX-License-Identifier: GPL-3.0-or-later

/usr/bin/podman run --name=mysql-achd -d \
    --restart=unless-stopped  \
    --pod achdpod \
    --volume systemd-mysql-achd:/var/lib/mysql \
    --secret achd-md,type=env,target=MYSQL_DATABASE \
    --secret achd-mu,type=env,target=MYSQL_USER \
    --secret achd-mp,type=env,target=MYSQL_PASSWORD \
    --secret achd-mrp,type=env,target=MYSQL_ROOT_PASSWORD \
    docker.io/library/mysql:8.3.0
    #--ip 192.168.5.10 \
    #--restart=unless-stopped \
    #--replace --rm \
    #--cgroups=split \
    #--network=achdnet \
    #--sdnotify=conmon \
    #--rm \
