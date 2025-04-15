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
from typing import Literal

from kaajal.__about__ import __appauthor__
from kaajal.__about__ import __appname__
from platformdirs import user_config_dir

logger = logging.getLogger(__name__)

config: dict[str, str | int | bool | Literal["%", "{", "$"]] = {
    "user": "",
    "password": "",
    "host": "",
    "ssh_key": "",
    "ssh_config": "",
    "ssh_config_host": "",
    "method": "",
    "gui": False,
    "os": "",
    "log_level": logging.WARNING,
    "log_file": "",
    "log_format": "{asctime:s} {levelname:<8s}:{name:<15s}: {message:s}",
    "log_style": "{",
    "log_datefmt": "%Y-%m-%d %H:%M:%S",
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


def read_config_env() -> None:
    """Read configuration from environment variables"""

    global config

    user = os.environ.get("KAAJAL_USER")
    password = os.environ.get("KAAJAL_PASSWORD")
    host = os.environ.get("KAAJAL_HOST")
    ssh_key = os.environ.get("KAAJAL_SSH_KEY")
    ssh_config = os.environ.get("KAAJAL_SSH_CONFIG")
    ssh_config_host = os.environ.get("KAAJAL_SSH_CONFIG_HOST")

    if user:
        config["user"] = user
    if password:
        config["password"] = password
    if host:
        config["host"] = host
    if ssh_key:
        config["ssh_key"] = ssh_key
    if ssh_config:
        config["ssh_config"] = ssh_config
    if ssh_config_host:
        config["ssh_config_host"] = ssh_config_host


def load(
    user: str | None = None,
    password: str | None = None,
    host: str | None = None,
    ssh_key: str | None = None,
    ssh_config: str | None = None,
    ssh_config_host: str | None = None,
) -> None:
    """
    Get configuration finding/reading it, in the next order
    1. $XDG_CONFIG_HOME:  $HOME/.config/kaajal
    2. virtual environemnt KAAJAL_XXXX
    3. command line
    """

    ucd = user_config_dir(appname=__appname__, appauthor=__appauthor__)

    # 1. $XDG_CONFIG_HOME:  $HOME/.config/kaajal
    if os.path.exists(ucd):
        config_file = os.path.join(ucd, "kaaja.conf")
        if os.path.exists(config_file):
            read_config_from(config_file)

        # logger.warning("Can not create config directory: " + ucd)
        # appname=__appname__, appauthor=__appauthor__, ensure_exists=True

    # 2. virtual environemnt KAAJAL_XXXX
    read_config_env()

    # 3. command line
    if user:
        config["user"] = user
    if password:
        config["password"] = password
    if host:
        config["host"] = host
    if ssh_key:
        config["ssh_key"] = ssh_key
    if ssh_config:
        config["ssh_config"] = ssh_config
    if ssh_config_host:
        config["ssh_config_host"] = ssh_config_host


def setup_log(log_level: str | None = None, log_file: str | None = None) -> None:
    """Setup the way we log the application"""

    global config

    if log_level:
        log_level = log_level.lower()
        if log_level == "notset":
            config["log_level"] = logging.NOTSET
        elif log_level == "debug":
            config["log_level"] = logging.DEBUG
        elif log_level == "info":
            config["log_level"] = logging.INFO
        elif log_level == "warning":
            config["log_level"] = logging.WARNING
        elif log_level == "error":
            config["log_level"] = logging.ERROR
        elif log_level == "critical":
            config["log_level"] = logging.CRITICAL

    if log_file:
        config["log_file"] = log_file
        logging.basicConfig(
            filename=log_file,
            level=config["log_level"],
            format=str(config["log_format"]),
            style=config["log_style"],  # type: ignore[arg-type]
            datefmt=str(config["log_datefmt"]),
        )
    else:
        logging.basicConfig(
            level=config["log_level"],
            format=str(config["log_format"]),
            style=config["log_style"],  # type: ignore[arg-type]
            datefmt=str(config["log_datefmt"]),
        )
