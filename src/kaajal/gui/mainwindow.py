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
        """Class constructor of Main Window"""
        logger.info("Staring Kaajal main window")

        tk.Tk.__init__(self, className="Kaajal")

        self.title(__appname__ + " " + __version__)
        self.geometry("640x480")
        self.minsize(400, 200)
        self.maxsize(800, 600)

        self._create_menus()

    def _create_menus(self) -> None:
        """Create menus for the window"""

        self.option_add("*tearOff", tk.FALSE)

        # ttk.Entry(self).grid()
        menubar = tk.Menu(self)
        # self["menu"] = menubar
        self.config(menu=menubar)
        # self._menus = {}  # type: Dict[str, tk.Menu]
        menu_file = tk.Menu(menubar)
        menu_edit = tk.Menu(menubar)

        menubar.add_cascade(menu=menu_file, label="File", underline=0)
        menubar.add_cascade(menu=menu_edit, label="Edit", underline=0)

        menu_file.add_command(label="New")
        menu_file.add_command(label="Open")
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self._exit_app)

    def _exit_app(self) -> None:
        self.quit()
