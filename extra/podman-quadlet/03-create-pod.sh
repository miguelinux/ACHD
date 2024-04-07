#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh
#
# SPDX-License-Identifier: GPL-3.0-or-later

podman pod create --label app=achd \
  --infra-name=achdinfra \
  --publish 3306:3306 \
  --publish 5000:5000 \
  --network=achdnet \
  --name achdpod
