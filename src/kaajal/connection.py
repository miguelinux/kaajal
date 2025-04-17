# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal connection functions"""

import logging

import paramiko
from paramiko.config import SSHConfig

logger = logging.getLogger(__name__)


class SSHConnection:
    """SSH Connection class"""

    def __init__(self) -> None:
        """Class constructor of SSH Connection"""

        self.config = SSHConfig()
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # nosec B507

    def connect(self, config) -> None:
        """Connect to the server"""

        if config["connection_type"] == "User":
            if config["user"] and config["host"] and config["password"]:
                pass
            else:
                logger.error('Missing arguments in "User" connetion type')
        elif config["connection_type"] == "SSH key":
            if config["user"] and config["host"] and config["ssh_key"]:
                pass
            else:
                logger.error('Missing arguments in "SSH key" connetion type')
        elif config["connection_type"] == "SSH host":
            if config["ssh_config"] and config["ssh_config_host"]:
                pass
            else:
                logger.error('Missing arguments in "SSH host" connetion type')
        else:
            logger.error("No connection type setted")
