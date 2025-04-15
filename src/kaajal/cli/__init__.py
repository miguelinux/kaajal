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
from kaajal.__about__ import __version__
from kaajal.gui import kaajalw

logger = logging.getLogger(__name__)


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="kaajal")
@click.option(
    "--gui/--no-gui", default=True, help="Use GUI version, enabled by default."
)
def kaajal(gui) -> int:
    """Main entry of the program"""
    my_system_os = system()

    display = "Allow GUI"
    # On Linux DISPLAY environment variable is used only with GUI
    if my_system_os == "Linux":
        display = os.environ.get("DISPLAY", "")

    if gui and display:
        kaajalw()
    else:
        click.echo("NO gui")

    return 0
