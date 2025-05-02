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

    def identify(self) -> None:
        """Identify the Linux distro"""

        if not self.ssh_conn:
            return

        # Get OS info
        self.ssh_conn.exec("cat /etc/os-release")

        if self.ssh_conn.std[1].channel.recv_exit_status():
            logger.warning(self.ssh_conn.std[2].read().decode("utf-8").strip())
            return

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
            output = self.ssh_conn.std[2].read().decode("utf-8").strip()
            if output.startswith("Sorry"):
                logger.warning(output)
            else:
                self.sudo = "sudo"

        logger.info("Linux %s", self.pretty_name)
