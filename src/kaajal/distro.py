# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal Linux distro functions"""

import logging
import os
from typing import Optional

from kaajal.connection import SSHConnection

logger = logging.getLogger(__name__)


class Distro:
    """Linux Distro class"""

    def __init__(self) -> None:
        """Class constructor of Linux distro"""

        self.id = ""
        self.name = ""
        self.pretty_name = ""
        # package manager
        self.pm = ""
        self.uid = ""
        self.sudo = ""
        self.ssh_conn: Optional[SSHConnection] = None

    def set_ssh_conn(self, conn: SSHConnection) -> None:
        """Set the SSH connection object"""

        if conn:
            self.ssh_conn = conn

    def identify(self) -> str:
        """Identify the Linux distro"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if not self.ssh_conn.is_connected:
            return_message = "No SSH connection"
            logger.warning(return_message)
            return return_message

        # Get OS info
        self.ssh_conn.exec("cat /etc/os-release")

        # if command returned non-zero exit status
        if self.ssh_conn.std[1].channel.recv_exit_status():
            return_message = self.ssh_conn.std[2].read().decode("utf-8").strip()
            logger.warning(return_message)
            return return_message

        output = self.ssh_conn.std[1].read().decode("utf-8").split("\n")

        for line in output:
            line = line.strip()
            values = line.split("=")

            if values[0] == "ID":
                self.id = values[1].replace('"', "")

            if values[0] == "NAME":
                self.name = values[1].replace('"', "")

            if values[0] == "PRETTY_NAME":
                self.pretty_name = values[1].replace('"', "")

        if self.id in ("centos", "fedora"):
            # package manager
            self.pm = "dnf"
        elif self.id in ("debian", "ubuntu"):
            # package manager
            self.pm = "apt-get"

        # Get User info
        self.ssh_conn.exec("id -u")
        self.uid = self.ssh_conn.std[1].read().decode("utf-8").strip()

        if self.uid != "0":
            self.ssh_conn.exec("sudo -l | grep -q NOPASSWD")
            # wait for exit status
            ret = self.ssh_conn.std[1].channel.recv_exit_status()
            if ret:
                return_message = "User can NOT run sudo without password"
                self.sudo = ""
                logger.warning(return_message)
            else:
                self.sudo = "sudo"

        logger.info("Linux %s", self.pretty_name)
        logger.debug('sudo = "%s"', self.sudo)

        return return_message

    def update(self) -> str:
        """Update the Linux distro"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if not self.ssh_conn.is_connected:
            return_message = "No SSH connection"
            logger.warning(return_message)
            return return_message

        if self.uid != "0" and not self.sudo:
            return_message = "User is not allowed to update the system"
            logger.warning(return_message)
            return return_message

        self._setup_proxy(self.pm)

        logger.info("%s -y update", self.pm)
        return_message = self.ssh_conn.exec(self.sudo + " " + self.pm + " -y update")

        # wait for exit status
        ret = self.ssh_conn.std[1].channel.recv_exit_status()
        if ret:
            logger.warning("Non zero return on %s -y update", self.pm)

        if return_message:
            logger.warning(return_message)

        if self.id in ("debian", "ubuntu"):
            logger.info("%s -y upgrade", self.pm)
            return_message = self.ssh_conn.exec(
                self.sudo + " " + self.pm + " -y upgrade"
            )

            # wait for exit status
            ret = self.ssh_conn.std[1].channel.recv_exit_status()
            if ret:
                logger.warning("Non zero return on %s -y upgrade", self.pm)

            if return_message:
                logger.warning(return_message)

        return return_message

    def install(self, str_pkgs_list: str = "", pkg_list_path: str = "") -> str:
        """Install new packages in Linux distro"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if not self.ssh_conn.is_connected:
            return_message = "No SSH connection"
            logger.warning(return_message)
            return return_message

        if self.uid != "0" and not self.sudo:
            return_message = "User is not allowed to update the system"
            logger.warning(return_message)
            return return_message

        if pkg_list_path:
            if os.path.exists(pkg_list_path):
                with open(pkg_list_path, encoding="utf-8") as pkg_list_file:
                    for line in pkg_list_file:
                        if not line or not line.strip():
                            continue
                        if line.strip()[0] == "#":
                            continue

                        str_pkgs_list += line.strip() + " "
            else:
                return_message = pkg_list_path + ": not found"
                logger.warning(return_message)
                return return_message

        if not str_pkgs_list:
            return_message = "No packages provided to install"
            logger.warning(return_message)
            return return_message

        logger.info("%s -y install %s", self.pm, str_pkgs_list)
        return_message = self.ssh_conn.exec(
            self.sudo + " " + self.pm + " -y install " + str_pkgs_list
        )
        # wait for exit status
        ret = self.ssh_conn.std[1].channel.recv_exit_status()
        if ret:
            logger.warning(
                "Non zero return on %s -y install %s", self.pm, str_pkgs_list
            )

        if return_message:
            logger.warning(return_message)

        return return_message

    def create_new_user(
        self,
        user: str = "",
        password: str = "",
        ssh_key: str = "",
        github_token: str = "",
    ) -> str:  # nosec B107 hardcoded_password_default
        """Create a new user in Linux distro"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if not self.ssh_conn.is_connected:
            return_message = "No SSH connection"
            logger.warning(return_message)
            return return_message

        if self.uid != "0" and not self.sudo:
            return_message = "User is not allowed to update the system"
            logger.warning(return_message)
            return return_message

        print(user)
        print(password)
        print(ssh_key)
        print(github_token)

        return return_message

    def _setup_proxy(self, target: str = "") -> None:
        """Set proxy if it is set in environment variables"""

        if not target:
            return

        if not self.ssh_conn:
            return

        http_proxy = os.environ.get("http_proxy")
        if not http_proxy:
            http_proxy = os.environ.get("HTTP_PROXY")

        https_proxy = os.environ.get("https_proxy")
        if not https_proxy:
            https_proxy = os.environ.get("HTTPS_PROXY")

        no_proxy = os.environ.get("no_proxy")
        if not no_proxy:
            no_proxy = os.environ.get("NO_PROXY")

        if http_proxy:
            logger.debug('http_proxy = "%s"', http_proxy)
        if https_proxy:
            logger.debug('https_proxy = "%s"', https_proxy)
        if no_proxy:
            logger.debug('no_proxy = "%s"', no_proxy)

        if target == "dnf":
            if http_proxy:
                self.ssh_conn.exec("grep -q proxy /etc/dnf/dnf.conf")
                if self.ssh_conn.std[1].channel.recv_exit_status():
                    cmd = "echo proxy=" + http_proxy
                    cmd += " | " + self.sudo + " tee -a /etc/dnf/dnf.conf"
                    self.ssh_conn.exec(cmd)
                    logger.debug("set http_proxy to dnf.conf")
