# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Kaajal connection functions"""

import logging

import paramiko
from paramiko.config import SSHConfig

logger = logging.getLogger(__name__)


class SSHConnection:
    """SSH Connection class"""

    def __init__(self) -> None:
        """Class constructor of SSH Connection"""

        self.config = SSHConfig()
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # nosec B507
