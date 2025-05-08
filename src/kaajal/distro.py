# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal Linux distro functions"""

import logging
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
        self.package_manager = ""
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
            self.package_manager = "dnf"
        elif self.id in ("debian", "ubuntu"):
            self.package_manager = "apt"

        # Get User info
        self.ssh_conn.exec("id -u")
        self.uid = self.ssh_conn.std[1].read().decode("utf-8").strip()

        if self.uid != "0":
            self.ssh_conn.exec("sudo -v")
            return_message = self.ssh_conn.std[2].read().decode("utf-8").strip()
            if return_message.startswith("Sorry"):
                logger.warning(return_message)
            else:
                self.sudo = "sudo"

        logger.info("Linux %s", self.pretty_name)

        return return_message

    def update(self) -> str:
        """Update the Linux distro"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if self.uid != "0" and not self.sudo:
            return_message = "User is not allowed to update the system"
            logger.warning(return_message)
            return return_message

        if self.id in ("centos", "fedora"):
            logger.info("dnf -y update")
            return_message = self.ssh_conn.exec(self.sudo + " dnf -y update")

            # wait for exit status
            ret = self.ssh_conn.std[1].channel.recv_exit_status()
            if ret:
                logger.warning("Non zero return on dnf -y update")

        elif self.id in ("debian", "ubuntu"):
            logger.info("apt-get -y update")
            return_message = self.ssh_conn.exec(self.sudo + " apt-get -y update")

            if return_message:
                logger.warning(return_message)

            # wait for exit status
            ret = self.ssh_conn.std[1].channel.recv_exit_status()
            if ret:
                logger.warning("Non zero return on apt-get -y update")

            logger.info("apt-get -y upgrade")
            return_message = self.ssh_conn.exec(self.sudo + " apt-get -y upgrade")

            # wait for exit status
            ret = self.ssh_conn.std[1].channel.recv_exit_status()
            if ret:
                logger.warning("Non zero return on apt-get -y upgrade")

        if return_message:
            logger.warning(return_message)

        return return_message

    def install(self, *pkgs) -> str:
        """Install new packages in Linux distro"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if self.uid != "0" and not self.sudo:
            return_message = "User is not allowed to update the system"
            logger.warning(return_message)
            return return_message

        if len(pkgs) == 0:
            return_message = "No packages provided to install"
            logger.warning(return_message)
            return return_message

        str_pkgs = " ".join(pkgs)

        if self.id in ("centos", "fedora"):
            logger.info("dnf -y install %s", str_pkgs)
            return_message = self.ssh_conn.exec(
                self.sudo + " dnf -y install " + str_pkgs
            )
            # wait for exit status
            ret = self.ssh_conn.std[1].channel.recv_exit_status()
            if ret:
                logger.warning("Non zero return on dnf -y install %s", str_pkgs)

        elif self.id in ("debian", "ubuntu"):
            logger.info("apt-get -y install")
            return_message = self.ssh_conn.exec(
                self.sudo + " apt-get -y install " + str_pkgs
            )
            # wait for exit status
            ret = self.ssh_conn.std[1].channel.recv_exit_status()
            if ret:
                logger.warning("Non zero return on apt-get -y install %s", str_pkgs)

        if return_message:
            logger.warning(return_message)

        return return_message

    def create_new_user(self) -> str:
        """Create a new user in Linux distro"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if self.uid != "0" and not self.sudo:
            return_message = "User is not allowed to update the system"
            logger.warning(return_message)
            return return_message

        return return_message
