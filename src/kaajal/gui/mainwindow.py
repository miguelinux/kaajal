# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main window GUI"""

import logging
import tkinter as tk

from kaajal.__about__ import __appname__
from kaajal.__about__ import __version__

logger = logging.getLogger(__name__)


class MainWindow(tk.Tk):
    """Kaajal main window"""

    def __init__(self) -> None:
        logger.info("Staring Kaajal main window")

        tk.Tk.__init__(self, className="Kaajal")

        self.title(__appname__ + " " + __version__)
        self.geometry("640x480")
        self.minsize(400, 200)
        self.maxsize(800, 600)
