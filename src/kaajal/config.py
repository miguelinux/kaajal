# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal configure functions"""

import logging
import os
from typing import Optional


logger = logging.getLogger(__name__)

CONN_CONFIG_NAME = "connection.conf"
LOG_CONFIG_NAME = "logger.conf"
APP_CONFIG_NAME = "app.conf"


class Config:
    """Configuration class"""

    def __init__(self) -> None:
        """Class constructor of Config"""

        self.conn_config = {
            "user": "",
            "password": "",
            "host": "",
            "ssh_key": "",
            "ssh_config": "",
            "ssh_config_host": "",
            "connection_type": "",  # User, SSH key, SSH host
        }

        self.gui_config = {
            "gui": "no",
        }

        self.log_config = {
            "level": "WARNING",
            "filename": "",
            "format": "{asctime:s} {levelname:<8s}:{name:<22s}: {message:s}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "filter": "yes",
        }

        self.user_config_dir = ""

    def print_conn(self) -> None:
        logger.debug("user: %s", self.conn_config["user"])
        logger.debug("password: %s", self.conn_config["password"])
        logger.debug("host: %s", self.conn_config["host"])
        logger.debug("ssh_key: %s", self.conn_config["ssh_key"])
        logger.debug("ssh_config: %s", self.conn_config["ssh_config"])
        logger.debug("ssh_config_host: %s", self.conn_config["ssh_config_host"])
        logger.debug("connection_type: %s", self.conn_config["connection_type"])

    def set_user_config_dir(self, path: str) -> None:
        """Set user config dir"""
        self.user_config_dir = path
        logger.debug("set user config dir to: %s", self.user_config_dir)

    def read_config_from(self, path: str, config: dict) -> None:
        """Read configuration from a file located in path variable"""

        # the items are: variable and value (i.e. variable = value)
        two_items = 2
        values = {}

        if os.path.exists(path):
            with open(path, encoding="utf-8") as conf_file:
                for line in conf_file:
                    if not line or not line.strip():
                        continue
                    if line.strip()[0] == "#":
                        continue

                    item = line.split("=")
                    if len(item) == two_items:
                        values[item[0].strip().lower()] = item[1].strip()

            for key in config:
                if key in values:
                    config[key] = values[key]

        else:
            logger.warning("%s: not found", path)

    def _read_conn_config_env(self) -> None:
        """Read configuration from environment variables"""

        user = os.environ.get("KAAJAL_USER")
        password = os.environ.get("KAAJAL_PASSWORD")
        host = os.environ.get("KAAJAL_HOST")
        ssh_key = os.environ.get("KAAJAL_SSH_KEY")
        ssh_config = os.environ.get("KAAJAL_SSH_CONFIG")
        ssh_config_host = os.environ.get("KAAJAL_SSH_CONFIG_HOST")

        if user:
            self.conn_config["user"] = user
        if password:
            self.conn_config["password"] = password
        if host:
            self.conn_config["host"] = host
        if ssh_key:
            self.conn_config["ssh_key"] = ssh_key
        if ssh_config:
            self.conn_config["ssh_config"] = ssh_config
        if ssh_config_host:
            self.conn_config["ssh_config_host"] = ssh_config_host

    def load_conn_config(self, **kwargs) -> None:
        """
        Get configuration finding/reading it, in the next order
        1. $XDG_CONFIG_HOME:  $HOME/.config/kaajal
        2. virtual environemnt KAAJAL_XXXX
        3. command line
        """

        # 1. $XDG_CONFIG_HOME:  $HOME/.config/kaajal
        if os.path.exists(self.user_config_dir):
            config_file_path = os.path.join(self.user_config_dir, CONN_CONFIG_NAME)
            if os.path.exists(config_file_path):
                self.read_config_from(config_file_path, self.conn_config)

        # 2. virtual environemnt KAAJAL_XXXX
        self._read_conn_config_env()

        # 3. command line
        if kwargs.get("user"):
            self.conn_config["user"] = kwargs["user"]
        if kwargs.get("password"):
            self.conn_config["password"] = kwargs["password"]
        if kwargs.get("host"):
            self.conn_config["host"] = kwargs["host"]
        if kwargs.get("ssh_key"):
            self.conn_config["ssh_key"] = kwargs["ssh_key"]
        if kwargs.get("ssh_config"):
            self.conn_config["ssh_config"] = kwargs["ssh_config"]
        if kwargs.get("ssh_config_host"):
            self.conn_config["ssh_config_host"] = kwargs["ssh_config_host"]

        self.get_conn_type()

    def load_log_config(
        self, log_level: Optional[str] = None, log_file: Optional[str] = None
    ) -> None:
        """Setup the way we log the application"""

        if os.path.exists(self.user_config_dir):
            config_file_path = os.path.join(self.user_config_dir, LOG_CONFIG_NAME)
            if os.path.exists(config_file_path):
                self.read_config_from(config_file_path, self.log_config)

        if log_level:
            level_num = logging.getLevelName(log_level.upper())
            if isinstance(level_num, int):
                self.log_config["level"] = logging.getLevelName(level_num)

        if log_file is not None:
            self.log_config["filename"] = log_file

        local_config = self.log_config.copy()

        if not local_config.get("filename"):
            local_config.pop("filename")

        # Remove filter from local config
        do_filter = local_config.pop("filter", "no")

        logging.basicConfig(**local_config)  # type: ignore[arg-type]

        if "no" != do_filter.lower():
            filter = logging.Filter("kaajal")
            logging.root.handlers[0].addFilter(filter)

    def get_conn_type(self) -> str:
        """Get the connection type based on current conn_config:
        User, SSH key or SSH host
        """

        if self.conn_config["connection_type"] == "User":
            if (
                self.conn_config["user"]
                and self.conn_config["host"]
                and self.conn_config["password"]
            ):
                return "User"

        if self.conn_config["connection_type"] == "SSH key":
            if (
                self.conn_config["user"]
                and self.conn_config["host"]
                and self.conn_config["ssh_key"]
            ):
                return "SSH key"

        if self.conn_config["connection_type"] == "SSH host":
            if self.conn_config["ssh_config"] and self.conn_config["ssh_config_host"]:
                return "SSH host"

        ret = ""

        if self.conn_config["user"] and self.conn_config["host"]:
            if self.conn_config["password"]:
                ret = "User"
            elif self.conn_config["ssh_key"]:
                ret = "SSH key"
        elif self.conn_config["ssh_config"] and self.conn_config["ssh_config_host"]:
            ret = "SSH host"

        self.conn_config["connection_type"] = ret
        return ret

    def set_conn_config(self, cfg_arg: dict) -> None:
        """Set the value of the config using a dictionary as argument"""
        for key in self.conn_config:
            if key in cfg_arg:
                self.conn_config[key] = cfg_arg[key]

    def save_conn_config(self) -> None:
        """Save the conn_config to the default location"""

        if not os.path.exists(self.user_config_dir):
            os.makedirs(self.user_config_dir, mode=0o750)
            if not os.path.exists(self.user_config_dir):
                logger.warning("%s: Can not create directory.", self.user_config_dir)
                return

        config_path = os.path.join(self.user_config_dir, CONN_CONFIG_NAME)

        str_content = "# Autosaved connection config\n"
        str_content += "# vi: set filetype=sh shiftwidth=4 tabstop=8 expandtab:\n#\n"
        str_content += "# User to configure the platform\n"
        str_content += "USER=" + self.conn_config["user"] + "\n\n"
        str_content += "# User passowrd\n"
        str_content += "PASSWORD=" + self.conn_config["password"] + "\n\n"
        str_content += "# Remote Host IP or DNS name\n"
        str_content += "HOST=" + self.conn_config["host"] + "\n\n"
        str_content += "# User SSH key to connect to the platform\n"
        str_content += "SSH_KEY=" + self.conn_config["ssh_key"] + "\n\n"
        str_content += "# User SSH self.conn_config file\n"
        str_content += "SSH_CONFIG=" + self.conn_config["ssh_config"] + "\n\n"
        str_content += "# Host from the user SSH config file\n"
        str_content += "SSH_CONFIG_HOST=" + self.conn_config["ssh_config_host"] + "\n\n"
        str_content += "# Type of connection to use (User, SSH key or SSH host)\n"
        str_content += "CONNECTION_TYPE=" + self.conn_config["connection_type"] + "\n"

        with open(config_path, mode="w", encoding="utf-8") as conf_file:
            conf_file.write(str_content)
        logger.debug("Conn config saved at: %s", config_path)

    def save_log_config(self) -> None:
        """Save the log_config to the default location"""

        if not os.path.exists(self.user_config_dir):
            os.makedirs(self.user_config_dir, mode=0o750)
            if not os.path.exists(self.user_config_dir):
                logger.warning("%s: Can not create directory.", self.user_config_dir)
                return

        config_path = os.path.join(self.user_config_dir, LOG_CONFIG_NAME)

        str_content = "# Autosaved logger config\n"
        str_content += "# vi: set filetype=sh shiftwidth=4 tabstop=8 expandtab:\n#\n"
        str_content += "# Log level: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET\n"
        str_content += "LEVEL=" + self.log_config["level"] + "\n\n"
        str_content += "# Filename to save the log if any\n"
        str_content += "FILENAME=" + self.log_config["filename"] + "\n\n"
        str_content += "# Format to display the log\n"
        str_content += "FORMAT=" + self.log_config["format"] + "\n\n"
        str_content += "# Style of the format\n"
        str_content += "STYLE=" + self.log_config["style"] + "\n\n"
        str_content += "# Date format\n"
        str_content += "DATEFMT=" + self.log_config["datefmt"] + "\n"

        with open(config_path, mode="w", encoding="utf-8") as conf_file:
            conf_file.write(str_content)
        logger.debug("Conn config saved at: %s", config_path)


app_config = Config()
