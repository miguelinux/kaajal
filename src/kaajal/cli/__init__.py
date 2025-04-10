# SPDX-FileCopyrightText: 2025-present Miguel Bernal Marin <miguel.bernal.marin@linux.intel.com>
#
# SPDX-License-Identifier: MIT
import click

from kaajal.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="kaajal")
def kaajal():
    click.echo("Hello world!")
