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
            if self.ssh_conn.std[1].channel.recv_exit_status():
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
        if self.ssh_conn.std[1].channel.recv_exit_status():
            logger.warning("Non zero return on %s -y update", self.pm)

        if return_message:
            logger.warning(return_message)

        if self.id in ("debian", "ubuntu"):
            logger.info("%s -y upgrade", self.pm)
            return_message = self.ssh_conn.exec(
                self.sudo + " " + self.pm + " -y upgrade"
            )

            # wait for exit status
            if self.ssh_conn.std[1].channel.recv_exit_status():
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
        if self.ssh_conn.std[1].channel.recv_exit_status():
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

        if not user:
            return_message = "create_new_user: NO Username given"
            logger.warning(return_message)
            return return_message

        if not password and not ssh_key:
            return_message = "create_new_user: NO password or SSH key given"
            logger.warning(return_message)
            return return_message

        if ssh_key and not os.path.exists(ssh_key):
            return_message = f"create_new_user: {ssh_key} not found"
            logger.warning(return_message)
            return return_message

        if github_token and not os.path.exists(github_token):
            return_message = f"create_new_user: {github_token} not found"
            logger.warning(return_message)
            return return_message

        return_message = self.ssh_conn.exec(f"id {user}")

        if return_message:
            logger.warning(return_message)
            return return_message

        if 0 == self.ssh_conn.std[1].channel.recv_exit_status():
            return_message = f"create_new_user: {user} already exists"
            logger.warning(return_message)
            return return_message

        cmd = self.sudo + " useradd --shell /usr/bin/bash --create-home "
        cmd += "--home-dir /home/" + user + ' --comment "made by kaajal" '
        cmd += user

        return_message = self.ssh_conn.exec(cmd)

        if return_message:
            logger.warning(return_message)
            return return_message

        # if command returned non-zero exit status
        if self.ssh_conn.std[1].channel.recv_exit_status():
            return_message = self.ssh_conn.std[2].read().decode("utf-8").strip()
            logger.warning(return_message)
            return return_message

        log_info = 'User "' + user + '" created '

        if password:
            cmd = f'echo "{user}:{password}" | '
            cmd += self.sudo + " chpasswd"

            return_message = self.ssh_conn.exec(cmd)

            if return_message:
                logger.warning(return_message)
                return return_message

            # if command returned non-zero exit status
            if self.ssh_conn.std[1].channel.recv_exit_status():
                return_message = self.ssh_conn.std[2].read().decode("utf-8").strip()
                logger.warning(return_message)
                return return_message

            log_info += "with password "

        if ssh_key:
            return_message = self.copy_ssh_key(ssh_key, user)
            if return_message:
                return return_message
            log_info += "and SSH key "

        if github_token:
            return_message = self.copy_github_token(github_token, user)
            if return_message:
                return return_message
            log_info += "and GitHub Token"

        logger.info(log_info)
        return return_message

    def copy_ssh_key(self, ssh_key_path: str = "", user: str = "current") -> str:
        """Copy SSH key to authorized_keys"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if not self.ssh_conn.is_connected:
            return_message = "No SSH connection"
            logger.warning(return_message)
            return return_message

        if not ssh_key_path:
            return_message = "No SSH key given"
            logger.warning(return_message)
            return return_message

        if ssh_key_path and not os.path.exists(ssh_key_path):
            return_message = f"copy_ssh_key: {ssh_key_path} not found"
            logger.warning(return_message)
            return return_message

        user_home = ""
        use_sudo = ""

        if user != "current":
            if self.uid != "0" and not self.sudo:
                return_message = "User is not allowed to update the system"
                logger.warning(return_message)
                return return_message

            use_sudo = self.sudo

            cmd = "getent passwd " + user + " | cut -d : -f 6"
            self.ssh_conn.exec(cmd)

            user_home = self.ssh_conn.std[1].read().decode("utf-8").strip()

            if not user_home:
                return_message = f"copy_ssh_key: User {user} not found in the system"
                logger.warning(return_message)
                return return_message
        else:
            # if user is "current"
            user_home = self.ssh_conn.home

        cmd = use_sudo + " mkdir -m 700 -p " + user_home + "/.ssh"
        self.ssh_conn.exec(cmd)

        if self.ssh_conn.std[1].channel.recv_exit_status():
            return_message = "copy_ssh_key: error at create .ssh directory"
            logger.warning(return_message)
            return return_message

        with open(ssh_key_path, encoding="utf-8") as ssh_key_file:
            ssh_pub_key = ssh_key_file.read().strip()

        cmd = "echo " + ssh_pub_key
        cmd += " | " + use_sudo + " tee -a "
        cmd += user_home + "/.ssh/authorized_keys"
        self.ssh_conn.exec(cmd)

        if self.ssh_conn.std[1].channel.recv_exit_status():
            return_message = "copy_ssh_key: error at add key to authoriezed_keys"
            logger.warning(return_message)
            return return_message

        if user != "current":
            cmd = use_sudo + " chown -R " + user + ":" + user + " "
            cmd += user_home + "/.ssh"
            self.ssh_conn.exec(cmd)

        logger.info("Copied SSH key to authorized_keys")
        return return_message

    def copy_github_token(
        self, github_token_path: str = "", user: str = "current"
    ) -> str:  # nosec B107 hardcoded_password_default
        """Copy GitHub Token"""

        return_message = ""

        if not self.ssh_conn:
            return_message = "No connection configured"
            logger.warning(return_message)
            return return_message

        if not self.ssh_conn.is_connected:
            return_message = "No SSH connection"
            logger.warning(return_message)
            return return_message

        if not github_token_path:
            return_message = "No GitHub Token given"
            logger.warning(return_message)
            return return_message

        if github_token_path and not os.path.exists(github_token_path):
            return_message = f"copy_github_token: {github_token_path} not found"
            logger.warning(return_message)
            return return_message

        user_home = ""
        use_sudo = ""

        if user != "current":
            if self.uid != "0" and not self.sudo:
                return_message = "User is not allowed to update the system"
                logger.warning(return_message)
                return return_message

            use_sudo = self.sudo

            cmd = "getent passwd " + user + " | cut -d : -f 6"
            self.ssh_conn.exec(cmd)

            user_home = self.ssh_conn.std[1].read().decode("utf-8").strip()

            if not user_home:
                return_message = (
                    f"copy_github_token: User {user} not found in the system"
                )
                logger.warning(return_message)
                return return_message
        else:
            # if user is "current"
            user_home = self.ssh_conn.home

        cmd = use_sudo + " mkdir -m 700 -p " + user_home + "/.config/github"
        self.ssh_conn.exec(cmd)

        if self.ssh_conn.std[1].channel.recv_exit_status():
            return_message = (
                "copy_github_token: error at create .config/github directory"
            )
            logger.warning(return_message)
            return return_message

        with open(github_token_path, encoding="utf-8") as github_token_file:
            str_github_token = github_token_file.read().strip()

        cmd = "echo " + str_github_token
        cmd += " | " + use_sudo + " tee "
        cmd += user_home + "/.config/github/token"
        self.ssh_conn.exec(cmd)

        if self.ssh_conn.std[1].channel.recv_exit_status():
            return_message = "copy_github_token: error when adding token"
            logger.warning(return_message)
            return return_message

        if user != "current":
            cmd = use_sudo + " chown -R " + user + ":" + user + " "
            cmd += user_home + "/.config"
            self.ssh_conn.exec(cmd)

        logger.info("Copied GitHub Token")
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
                    # if the word proxy was not found in dnf.conf
                    cmd = "echo proxy=" + http_proxy
                    cmd += " | " + self.sudo + " tee -a /etc/dnf/dnf.conf"
                    self.ssh_conn.exec(cmd)
                    logger.debug("Set http_proxy to dnf.conf")
        elif target == "apt-get":
            if http_proxy:
                file_exist = self.ssh_conn.stat("/etc/apt/apt.conf.d/proxy.conf")
                if 1 != file_exist:
                    # if proxy.conf does not exist or has 0 size
                    cmd = 'echo Acquire::http::Proxy \\"' + http_proxy + '\\"\\; | '
                    cmd += self.sudo + " tee /etc/apt/apt.conf.d/proxy.conf"
                    self.ssh_conn.exec(cmd)
                    logger.debug("Set http_proxy to proxy.conf")
