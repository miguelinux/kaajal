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
from tkinter import filedialog
from tkinter import ttk
from tkinter.ttk import Widget

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
        # self.geometry("640x480")
        # self.minsize(400, 200)
        # self.maxsize(800, 600)

        self._create_menus()

        mainframe = ttk.Frame(self, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky="nwes")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.connection_type = tk.StringVar()
        lbl_conn = ttk.Label(mainframe, textvariable=self.connection_type)
        lbl_conn.configure(foreground="blue")
        lbl_conn.grid(column=2, row=1, sticky=tk.W)
        self.connection_type.set("Unknown")

        self.user = tk.StringVar()
        txt_user = ttk.Entry(mainframe, width=15, textvariable=self.user)
        txt_user.grid(column=2, row=2, sticky="we")

        self.password = tk.StringVar()
        txt_password = ttk.Entry(mainframe, width=15, textvariable=self.password)
        txt_password.grid(column=2, row=3, sticky="we")

        self.host = tk.StringVar()
        txt_host = ttk.Entry(mainframe, width=15, textvariable=self.host)
        txt_host.grid(column=2, row=4, sticky="we")

        self.ssh_key = tk.StringVar()
        txt_ssh_key = ttk.Entry(mainframe, width=15, textvariable=self.ssh_key)
        txt_ssh_key.grid(column=2, row=5, sticky="we")

        self.ssh_config = tk.StringVar()
        txt_ssh_config = ttk.Entry(mainframe, width=15, textvariable=self.ssh_config)
        txt_ssh_config.grid(column=2, row=6, sticky="we")

        self.ssh_config_host = tk.StringVar()
        txt_ssh_config_host = ttk.Entry(
            mainframe, width=15, textvariable=self.ssh_config_host
        )
        txt_ssh_config_host.grid(column=2, row=7, sticky="we")

        ttk.Label(mainframe, text="Conection type:").grid(column=1, row=1, sticky=tk.E)
        ttk.Label(mainframe, text="User:").grid(column=1, row=2, sticky=tk.W)
        ttk.Label(mainframe, text="Password:").grid(column=1, row=3, sticky=tk.W)
        ttk.Label(mainframe, text="Host:").grid(column=1, row=4, sticky=tk.W)
        ttk.Label(mainframe, text="SSH key:").grid(column=1, row=5, sticky=tk.W)
        ttk.Label(mainframe, text="SSH config:").grid(column=1, row=6, sticky=tk.W)
        ttk.Label(mainframe, text="SSH config host:").grid(column=1, row=7, sticky=tk.W)

        btn_ssh_key = ttk.Button(
            mainframe,
            text="Search SSH Key",
            command=lambda: self._open_file(self.ssh_key),
        )
        btn_ssh_key.grid(column=3, row=5, sticky="we")

        btn_ssh_config = ttk.Button(
            mainframe,
            text="Search SSH config",
            command=lambda: self._open_file(self.ssh_config),
        )
        btn_ssh_config.grid(column=3, row=6, sticky="we")

        ttk.Button(mainframe, text="Connect").grid(column=1, row=9, sticky=tk.W)

        self.conn_user = (
            txt_user,
            txt_password,
            txt_host,
        )
        self.conn_ssh_key = (
            txt_user,
            txt_host,
            txt_ssh_key,
            btn_ssh_key,
        )
        self.conn_ssh_host = (
            txt_ssh_config,
            txt_ssh_config_host,
            btn_ssh_config,
        )

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def _create_menus(self) -> None:
        """Create menus for the window"""

        self.option_add("*tearOff", tk.FALSE)

        # ttk.Entry(self).grid()
        menubar = tk.Menu(self)
        # self["menu"] = menubar
        self.config(menu=menubar)
        # self._menus = {}  # type: Dict[str, tk.Menu]
        menu_file = tk.Menu(menubar)
        menu_conn = tk.Menu(menubar)

        menubar.add_cascade(menu=menu_file, label="File", underline=0)
        menubar.add_cascade(menu=menu_conn, label="Connection", underline=1)

        menu_file.add_command(label="Exit", command=self._exit_app)

        menu_conn.add_command(label="User", command=lambda: self.set_conn_type("user"))
        menu_conn.add_command(
            label="SSH Key", command=lambda: self.set_conn_type("ssh_key")
        )
        menu_conn.add_command(
            label="SSH Host", command=lambda: self.set_conn_type("ssh_host")
        )

    def _exit_app(self) -> None:
        """Exit from the app"""
        self.quit()

    def _open_file(self, strVar: tk.StringVar) -> None:
        str_filename = filedialog.askopenfilename()
        if str_filename:
            strVar.set(str_filename)

    def fill_txt_values(self, config: dict) -> None:
        """Fill the txt fields with config values"""
        if config["user"]:
            self.user.set(config["user"])
        if config["password"]:
            self.password.set(config["password"])
        if config["host"]:
            self.host.set(config["host"])
        if config["ssh_key"]:
            self.ssh_key.set(config["ssh_key"])
        if config["ssh_config"]:
            self.ssh_config.set(config["ssh_config"])
        if config["ssh_config_host"]:
            self.ssh_config_host.set(config["ssh_config_host"])

    def set_conn_type(self, conn_type: str) -> None:
        """Set the GUI to the conn_type"""

        widget: Widget | None = None

        for widget in self.conn_user:
            widget.config(state="disabled")
        for widget in self.conn_ssh_key:
            widget.config(state="disabled")
        for widget in self.conn_ssh_host:
            widget.config(state="disabled")

        self.connection_type.set(conn_type)

        if conn_type == "SSH key":
            for widget in self.conn_ssh_key:
                widget.config(state="normal")
        elif conn_type == "SSH host":
            for widget in self.conn_ssh_host:
                widget.config(state="normal")
        else:
            # If none of above then use user
            self.connection_type.set("User")
            for widget in self.conn_user:
                widget.config(state="normal")
