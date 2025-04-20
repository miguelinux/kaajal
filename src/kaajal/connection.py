# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal connection functions"""

import logging
import os
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

        connect_args = {
            "hostname": "",
            "username": "",
            "port": 22,
            "timeout": 15,
        }

        if config["connection_type"] == "User":
            if config["user"] and config["host"] and config["password"]:
                connect_args["hostname"] = config["host"]
                connect_args["username"] = config["user"]
                connect_args["password"] = config["password"]
                error_message = self._connect(**connect_args)
            else:
                error_message = 'Missing arguments in "User" connetion type'
                logger.error(error_message)

        elif config["connection_type"] == "SSH key":
            if config["user"] and config["host"] and config["ssh_key"]:
                if os.path.exists(config["ssh_key"]):
                    connect_args["hostname"] = config["host"]
                    connect_args["username"] = config["user"]
                    connect_args["key_filename"] = config["ssh_key"]
                    error_message = self._connect(**connect_args)
                else:
                    error_message = config["ssh_key"] + ": Not found."
                    logger.error(error_message)
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

    def _connect(self, **kwargs) -> str:
        """SSH Connect using user and password"""

        return_message = ""

        if self.is_connected:
            return_message = "You are already connected."
            return return_message

        try:
            self.client.connect(**kwargs)

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
