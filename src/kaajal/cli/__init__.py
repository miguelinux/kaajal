# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main kaajal module file"""

import logging
import os
from platform import system

import click
from kaajal import my_setup
from kaajal.__about__ import __appname__
from kaajal.__about__ import __version__
from kaajal.config import config
from kaajal.gui import kaajalw

logger = logging.getLogger(__name__)


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name=__appname__)
@click.option(
    "--gui/--no-gui", default=True, help="Use GUI version, enabled by default."
)
@click.option("-u", "--user", help="User to connect to the remote host")
@click.option("-p", "--password", help="Password to connect to the remote host")
@click.option("--host", help="Host or IP to connect to remote host ")
@click.option("-k", "--ssh-key", help="SSH key file used to connect to remote host")
@click.option("--ssh-config", help="SSH config file")
@click.option("--ssh-config-host", help="Host from SSH config file")
@click.option(
    "-l",
    "--log-level",
    help="Log level (notset, debug, info, warning, error, critical)",
)
@click.option("--log-file", help="Filename to save logs")
def kaajal(
    gui, user, password, host, ssh_key, ssh_config, ssh_config_host, log_level, log_file
) -> int:
    """Main entry of the program"""
    my_system_os = system()
    config["os"] = my_system_os

    if log_level:
        log_level = log_level.lower()
        if log_level == "notset":
            config["log_level"] = logging.NOTSET
        elif log_level == "debug":
            config["log_level"] = logging.DEBUG
        elif log_level == "info":
            config["log_level"] = logging.INFO
        elif log_level == "warning":
            config["log_level"] = logging.WARNING
        elif log_level == "error":
            config["log_level"] = logging.ERROR
        elif log_level == "critical":
            config["log_level"] = logging.CRITICAL

    if log_file:
        config["log_file"] = log_file
        logging.basicConfig(
            filename=log_file,
            level=config["log_level"],
            format=str(config["log_format"]),
            style=config["log_style"],  # type: ignore[arg-type]
            datefmt=str(config["log_datefmt"]),
        )
    else:
        logging.basicConfig(
            level=config["log_level"],
            format=str(config["log_format"]),
            style=config["log_style"],  # type: ignore[arg-type]
            datefmt=str(config["log_datefmt"]),
        )

    display = "Allow GUI"
    # On Linux DISPLAY environment variable is used only with GUI
    if my_system_os == "Linux":
        display = os.environ.get("DISPLAY", "")

    if gui and display:
        config["gui"] = True
        kaajalw()
    else:
        my_setup()

    return 0
