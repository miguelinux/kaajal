# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal common functions"""

import logging

from kaajal.config import app_config
from kaajal.connection import SSHConnection
from kaajal.distro import Distro

# from simple_term_menu import TerminalMenu

logger = logging.getLogger(__name__)


def close_all(conn: SSHConnection) -> None:
    conn.close()
    app_config.save_conn_config()
    app_config.save_log_config()


def cli_main() -> None:
    """Ensure everething is setup well"""

    if not app_config.get_conn_type():
        print("do setup")

    ssh_conn = SSHConnection()
    distro = Distro()
    distro.set_ssh_conn(ssh_conn)

    error_msg = ssh_conn.connect(app_config.conn_config)

    if error_msg:
        close_all(ssh_conn)
        return

    error_msg = distro.identify()

    if error_msg and not error_msg.startswith("Sorry"):
        return

    close_all(ssh_conn)
