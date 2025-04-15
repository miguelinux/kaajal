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

from kaajal.__about__ import __appauthor__
from kaajal.__about__ import __appname__
from platformdirs import user_config_dir

logger = logging.getLogger(__name__)

my_config = {
    "user": "",
    "passwd": "",
    "host": "",
    "ssh_key": "",
    "ssh_config": "",
    "ssh_config_host": "",
    "method": "",
}


def read_config() -> None:
    """Read config file if exist, is it does not exist create it"""

    ucd = user_config_dir(
        appname=__appname__, appauthor=__appauthor__, ensure_exists=True
    )

    if not os.path.exists(ucd):
        logger.warning("Can not create config directory: " + ucd)
        return

    print("ok")
