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

import platformdirs
from kaajal.__about__ import __appauthor__
from kaajal.__about__ import __appname__

logger = logging.getLogger(__name__)

config: dict[str, str | int | bool | Literal["%", "{", "$"]] = {
    "user": "",
    "password": "",
    "host": "",
    "ssh_key": "",
    "ssh_config": "",
    "ssh_config_host": "",
    "connection_type": "",  # User, SSH key, SSH host
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

        for key in config:
            if key in values:
                config[key] = values[key]

    else:
        logger.warning("%s: not found", path)


def read_config_env() -> None:
    """Read configuration from environment variables"""

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


def load(**kwargs) -> None:
    """
    Get configuration finding/reading it, in the next order
    1. $XDG_CONFIG_HOME:  $HOME/.config/kaajal
    2. virtual environemnt KAAJAL_XXXX
    3. command line
    """

    ucd = platformdirs.user_config_dir(appname=__appname__, appauthor=__appauthor__)

    # 1. $XDG_CONFIG_HOME:  $HOME/.config/kaajal
    if os.path.exists(ucd):
        config_file = os.path.join(ucd, "kaaja.conf")
        if os.path.exists(config_file):
            read_config_from(config_file)

    # 2. virtual environemnt KAAJAL_XXXX
    read_config_env()

    # 3. command line
    if kwargs.get("user"):
        config["user"] = kwargs["user"]
    if kwargs.get("password"):
        config["password"] = kwargs["password"]
    if kwargs.get("host"):
        config["host"] = kwargs["host"]
    if kwargs.get("ssh_key"):
        config["ssh_key"] = kwargs["ssh_key"]
    if kwargs.get("ssh_config"):
        config["ssh_config"] = kwargs["ssh_config"]
    if kwargs.get("ssh_config_host"):
        config["ssh_config_host"] = kwargs["ssh_config_host"]


def setup_log(log_level: str | None = None, log_file: str | None = None) -> None:
    """Setup the way we log the application"""

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


def get_conn_type() -> str:
    """Get the connection type based on current config:
    User, SSH key or SSH host
    """

    ret = ""
    if config["user"] and config["host"]:
        if config["password"]:
            ret = "User"
        elif config["ssh_key"]:
            ret = "SSH key"
    elif config["ssh_config"] and config["ssh_config_host"]:
        ret = "SSH host"

    config["connection_type"] = ret
    return ret


def set(cfg_arg: dict) -> None:
    for key in config:
        if key in cfg_arg:
            config[key] = cfg_arg[key]


def save() -> None:
    """Save the config to the default location"""

    ucd = platformdirs.user_config_dir(
        appname=__appname__, appauthor=__appauthor__, ensure_exists=True
    )
    if not os.path.exists(ucd):
        logger.warning("%s: Can not create directory.", ucd)
        return

    config_path = os.path.join(ucd, "kaaja.conf")

    str_content = "# Autosaved config\n"
    str_content += "# vi: set filetype=sh shiftwidth=4 tabstop=8 expandtab:\n#\n"
    str_content += "# User to configure the platform\n"
    str_content += "USER=" + config["user"] + "\n\n"
    str_content += "# User passowrd\n"
    str_content += "PASSWORD=" + config["password"] + "\n\n"
    str_content += "# Remote Host IP or DNS name\n"
    str_content += "HOST=" + config["host"] + "\n\n"
    str_content += "# User SSH key to connect to the platform\n"
    str_content += "SSH_KEY=" + config["ssh_key"] + "\n\n"
    str_content += "# User SSH config file\n"
    str_content += "SSH_CONFIG=" + config["ssh_config"] + "\n\n"
    str_content += "# Host from the user SSH config file\n"
    str_content += "SSH_CONFIG_HOST=" + config["ssh_config_host"] + "\n\n"
    str_content += "# Type of connection to use (User, SSH key or SSH host)\n"
    str_content += "CONNECTION_TYPE=" + config["connection_type"] + "\n"

    with open(config_path, mode="w", encoding="utf-8") as conf_file:
        conf_file.write(str_content)
