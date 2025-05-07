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
from kaajal import cli_main
from kaajal.__about__ import __appname__
from kaajal.__about__ import __version__
from kaajal.config import app_config

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
def kaajal(**kwargs) -> int:
    """Kaajal: setup a remote platform"""

    app_config.load_conn_config(**kwargs)

    app_config.load_log_config(kwargs["log_level"], kwargs["log_file"])

    my_system_os = system()

    display = "Allow GUI"
    # On Linux DISPLAY environment variable is used only with GUI
    if my_system_os == "Linux":
        display = os.environ.get("DISPLAY", "")

    if kwargs["gui"] and display:
        # Call gui lib only when we need it
        from kaajal.gui import kaajalw

        app_config.gui_config["gui"] = "yes"
        kaajalw(False)
    else:
        cli_main()

    return 0
