#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
#
# SPDX-License-Identifier: GPL-3.0-or-later

mkdir -p $HOME/.config/containers/systemd

cp achd.network mysql-achd.container mysql-achd.volume \
    $HOME/.config/containers/systemd

systemctl --user daemon-reload

if ! podman network ls | grep -q achdnet
then
    systemctl --user start achd-network.service
fi

if ! podman volume ls | grep -q mysql-achd
then
    systemctl --user start mysql-achd-volume.service
fi
