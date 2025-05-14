# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal cli functions"""

import logging

import click
from kaajal.config import app_config
from kaajal.connection import SSHConnection
from kaajal.distro import Distro

logger = logging.getLogger(__name__)


def close_all(conn: SSHConnection) -> None:
    conn.close()
    app_config.save_conn_config()
    app_config.save_log_config()


def ask_conn_value(prompt: str, key: str, hidden: bool = False) -> None:
    """Ask the config value"""
    value = app_config.conn_config[key]
    if value:
        value = click.prompt(prompt, default=value, hide_input=hidden)
    else:
        value = click.prompt(prompt, hide_input=hidden)
    app_config.conn_config[key] = value


def ask_for_parameters() -> None:
    """Ask for the missing parameters"""

    click.echo("  Please choose the connection type:\n")
    click.echo("1. User     (user, password, ip)")
    click.echo("2. SSH key  (user, ssh key, ip)")
    click.echo("3. SSH host (ssh config, ssh host)")
    option = click.prompt("Option", default=1, type=int)

    if option == 1:
        # User
        ask_conn_value("Username", "user")
        ask_conn_value("Password", "password", True)
        ask_conn_value("Host IP", "host")
        app_config.conn_config["connection_type"] = "User"
    elif option == 2:
        # SSH key
        ask_conn_value("Username", "user")
        ask_conn_value("Host IP", "host")
        ask_conn_value("Path to SSH key", "ssh_key")
        app_config.conn_config["connection_type"] = "SSH key"
    elif option == 3:
        # SSH host
        ask_conn_value("Path to SSH config", "ssh_config")
        ask_conn_value("Host ID in SSH confg", "ssh_config_host")
        app_config.conn_config["connection_type"] = "SSH host"


def cli_main() -> None:
    """Ensure everething is setup well"""

    if not app_config.get_conn_type():
        ask_for_parameters()

    ssh_conn = SSHConnection()
    distro = Distro()
    distro.set_ssh_conn(ssh_conn)

    error_msg = ssh_conn.connect(app_config.conn_config)

    if error_msg:
        close_all(ssh_conn)
        return

    error_msg = distro.identify()

    if error_msg and not error_msg.startswith("Sorry"):
        close_all(ssh_conn)
        return

    error_msg = distro.update()

    if error_msg:
        close_all(ssh_conn)
        return

    error_msg = distro.install("git tmux vim")

    if error_msg:
        close_all(ssh_conn)
        return

    close_all(ssh_conn)
