# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal configure functions"""

import logging
import os

from kaajal.__about__ import __appauthor__
from kaajal.__about__ import __appname__
from platformdirs import user_config_dir

logger = logging.getLogger(__name__)

config = {
    "user": "",
    "passwd": "",
    "host": "",
    "ssh_key": "",
    "ssh_config": "",
    "ssh_config_host": "",
    "method": "",
    "gui": False,
    "os": "",
    "log_level": logging.WARNING,
}


def read_config_from(path: str) -> None:
    """Read configuration from a file located in path variable"""

    global config

    # the items are: variable and value (i.e. variable = value)
    two_items = 2
    values = {}

    if os.path.exists(path):
        with open(path, encoding="utf-8") as conf_file:
            for line in conf_file:
                if not line or not line.strip():
                    continue
                if line.strip()[0] == "#":
                    continue

                item = line.split("=")
                if len(item) == two_items:
                    values[item[0].strip().lower()] = item[1].strip().lower()

        for val in config:
            if val in values:
                config[val] = values[val]

    else:
        logger.warning(f"{path}: not found")


def get_config() -> None:
    """
    Get configuration finding/reading it, in the next order
    1. $XDG_CONFIG_HOME:  $HOME/.config/kaajal
    2. virtual environemnt KAAJAL_XXXX
    3. command line
    """

    ucd = user_config_dir(
        appname=__appname__, appauthor=__appauthor__, ensure_exists=True
    )

    if not os.path.exists(ucd):
        logger.warning("Can not create config directory: " + ucd)

    config_file = os.path.join(ucd, "kaaja.conf")

    read_config_from(config_file)
