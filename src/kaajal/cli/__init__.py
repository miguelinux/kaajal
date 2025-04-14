# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main persea module file"""

import logging
from platform import system

import click
from kaajal.__about__ import __version__
from kaajal.gui.mainwindow import MainWindow

logger = logging.getLogger(__name__)


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="kaajal")
@click.option(
    "--gui/--no-gui", default=True, help="Use GUI version, enabled by default."
)
def kaajal(gui):
    """Main entry of the program"""
    my_system_os = system()

    if my_system_os == "Linux":
        click.echo("Linux")
    elif my_system_os == "Darwin":
        click.echo("Darwin")
    elif my_system_os == "Windows":
        click.echo("Windows")

    if gui:
        click.echo("gui")
        try:
            root = MainWindow()
            root.mainloop()
        # TODO: Test this on a no GUI environment
        except Exception:
            logger.exception("Internal launch or mainloop error")

    else:
        click.echo("NO gui")
