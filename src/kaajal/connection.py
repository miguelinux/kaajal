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
from typing import Any
from typing import Optional
from typing import Union

import paramiko
from paramiko.channel import ChannelFile
from paramiko.channel import ChannelStderrFile
from paramiko.channel import ChannelStdinFile
from paramiko.config import SSHConfig

logger = logging.getLogger(__name__)


class SSHConnection:
    """SSH Connection class"""

    def __init__(self) -> None:
        """Class constructor of SSH Connection"""

        self.config = SSHConfig()
        self.client = paramiko.SSHClient()

        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # nosec B507
        self.sftp: Optional[paramiko.SFTPClient] = None

        self.is_connected = False
        # stdin = 0, stdout = 1, stderr = 2
        self.std: Union[
            tuple[ChannelStdinFile, ChannelFile, ChannelStderrFile],
            tuple[(Any, Any, Any)],
        ] = (0, 1, 2)

    def close(self) -> None:
        """Close SSH connection"""
        if self.is_connected:
            self.client.close()
            self.is_connected = False
            logger.info("Closing SSH connection")

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
                # https://stackoverflow.com/questions/26712959/paramiko-connect-without-asking-ssh-key
                connect_args["look_for_keys"] = False
                connect_args["allow_agent"] = False
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
                if os.path.exists(config["ssh_config"]):
                    ssh_config = SSHConfig.from_path(config["ssh_config"])
                    host_config = ssh_config.lookup(config["ssh_config_host"])

                    if len(host_config) < 3:
                        error_message = (
                            config["ssh_config_host"]
                            + ", does not have enough entries."
                        )
                        logger.error(error_message)
                        return error_message

                    if "hostname" in host_config:
                        connect_args["hostname"] = host_config["hostname"]
                    else:
                        error_message = (
                            config["ssh_config_host"] + " (Hostname): not found."
                        )
                        logger.error(error_message)
                        return error_message

                    if "user" in host_config:
                        connect_args["username"] = host_config["user"]
                    else:
                        error_message = (
                            config["ssh_config_host"] + " (User): not found."
                        )
                        logger.error(error_message)
                        return error_message

                    if "identityfile" in host_config:
                        connect_args["key_filename"] = host_config["identityfile"]
                    else:
                        error_message = (
                            config["ssh_config_host"] + " (IdentityFile): not found."
                        )
                        logger.error(error_message)
                        return error_message

                    if "port" in host_config:
                        connect_args["port"] = int(host_config["port"])

                    if "connecttimeout" in host_config:
                        connect_args["timeout"] = float(host_config["connecttimeout"])

                    ##if 'proxycommand' in user_config:
                    ##    cfg['sock'] = paramiko.ProxyCommand(user_config['proxycommand'])

                    error_message = self._connect(**connect_args)
                else:
                    error_message = config["ssh_config"] + ": Not found."
                    logger.error(error_message)
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
            self.sftp = self.client.open_sftp()

            logger.info("SSH connected to %s", kwargs["hostname"])

        return return_message

    def exec(
        self, command, bufsize=-1, timeout=None, get_pty=False, environment=None
    ) -> str:
        """Execute a command on the SSH server"""

        return_message = ""

        if not self.is_connected:
            return "Not connected to a SSH server"

        if not command:
            return "Not command to execute given"

        try:
            self.std = self.client.exec_command(
                command, bufsize, timeout, get_pty, environment
            )  # nosec B601

        except paramiko.SSHException as e:
            return_message = "SSHException: " + str(e)
            logger.exception(return_message)

        return return_message
