# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal connection functions"""

import logging
import socket

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
        self.is_connected = False

    def close(self) -> None:
        """Close SSH connection"""
        if self.is_connected:
            self.client.close()

    def connect(self, config) -> str:
        """Connect to the server"""

        error_message = ""

        if config["connection_type"] == "User":
            if config["user"] and config["host"] and config["password"]:
                error_message = self._connect_user(
                    user=config["user"],
                    password=config["password"],
                    host=config["host"],
                )
            else:
                error_message = 'Missing arguments in "User" connetion type'
                logger.error(error_message)

        elif config["connection_type"] == "SSH key":
            if config["user"] and config["host"] and config["ssh_key"]:
                pass
            else:
                error_message = 'Missing arguments in "SSH key" connetion type'
                logger.error(error_message)

        elif config["connection_type"] == "SSH host":
            if config["ssh_config"] and config["ssh_config_host"]:
                pass
            else:
                error_message = 'Missing arguments in "SSH host" connetion type'
                logger.error(error_message)

        else:
            error_message = "No connection type setted"
            logger.error(error_message)

        return error_message

    def _connect_user(self, user: str, password: str, host: str) -> str:
        """SSH Connect using user and password"""

        return_message = ""

        if self.is_connected:
            return_message = "You are already connected."
            return return_message

        try:
            self.client.connect(hostname=host, username=user, password=password)

        except paramiko.AuthenticationException as e:
            return_message = "AuthenticationException: " + str(e)
            logger.exception(return_message)

        except paramiko.ssh_exception.NoValidConnectionsError as e:
            return_message = "NoValidConnectionsError: " + str(e)
            logger.exception(return_message)

        except paramiko.BadHostKeyException as e:
            return_message = "BadHostKeyException: " + str(e)
            logger.exception(return_message)

        except socket.error as e:
            return_message = "Socket Error: " + str(e)
            logger.exception(return_message)

        except paramiko.SSHException as e:
            return_message = "SSHException: " + str(e)
            logger.exception(return_message)

        else:
            self.is_connected = True

        return return_message


ssh_conn = SSHConnection()
