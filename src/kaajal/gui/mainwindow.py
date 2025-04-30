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
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Widget
from typing import Optional

from kaajal.__about__ import __appname__
from kaajal.__about__ import __version__
from kaajal.config import app_config
from kaajal.connection import SSHConnection

logger = logging.getLogger(__name__)


class MainWindow(tk.Tk):
    """Kaajal main window"""

    def __init__(self) -> None:
        """Class constructor of Main Window"""
        logger.info("Staring Kaajal main window")

        tk.Tk.__init__(self, className="Kaajal")

        self.title(__appname__ + " " + __version__)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._exit_app)

        self._create_menus()

        mainframe = ttk.Frame(self, padding="3 3 3 3")

        notebook = ttk.Notebook(mainframe)
        notebook.pack(expand=True, fill="both")

        conn_frame = ttk.Frame(notebook)
        # conn_frame.grid(column=0, row=0, sticky="nwes")

        r_user_frame = ttk.Frame(notebook)
        # conn_frame.grid(column=0, row=0, sticky="nwes")

        self.connection_type = tk.StringVar()
        self.user = tk.StringVar()
        self.password = tk.StringVar()
        self.host = tk.StringVar()
        self.ssh_key = tk.StringVar()
        self.ssh_config = tk.StringVar()
        self.ssh_config_host = tk.StringVar()
        self.str_status_bar = tk.StringVar()

        self._create_conn_frame(conn_frame)
        self._create_remote_user_frame(r_user_frame)

        lbl_status_bar = ttk.Label(mainframe, textvariable=self.str_status_bar)
        lbl_status_bar.configure(relief="sunken", anchor=tk.E)
        lbl_status_bar.pack(fill="x", side="bottom")

        notebook.add(conn_frame, text="Connection")
        notebook.add(r_user_frame, text="Remote User")
        mainframe.pack(expand=True, fill="both")

        self.ssh_conn = SSHConnection()

    def _create_conn_frame(self, frame: ttk.Frame) -> None:
        """Creation of the Connection frame"""

        lbl_conn = ttk.Label(frame, textvariable=self.connection_type)
        lbl_conn.configure(foreground="blue")
        lbl_conn.grid(column=2, row=1, sticky=tk.W)
        self.connection_type.set("Unknown")

        txt_user = ttk.Entry(frame, width=15, textvariable=self.user)
        txt_user.grid(column=2, row=2, sticky="we")

        txt_password = ttk.Entry(frame, width=15, textvariable=self.password)
        txt_password.grid(column=2, row=3, sticky="we")

        txt_host = ttk.Entry(frame, width=15, textvariable=self.host)
        txt_host.grid(column=2, row=4, sticky="we")

        txt_ssh_key = ttk.Entry(frame, width=15, textvariable=self.ssh_key)
        txt_ssh_key.grid(column=2, row=5, sticky="we")

        txt_ssh_config = ttk.Entry(frame, width=15, textvariable=self.ssh_config)
        txt_ssh_config.grid(column=2, row=6, sticky="we")

        txt_ssh_config_host = ttk.Entry(
            frame, width=15, textvariable=self.ssh_config_host
        )
        txt_ssh_config_host.grid(column=2, row=7, sticky="we")

        ttk.Label(frame, text="Conection type:").grid(column=1, row=1, sticky=tk.E)
        ttk.Label(frame, text="User:").grid(column=1, row=2, sticky=tk.W)
        ttk.Label(frame, text="Password:").grid(column=1, row=3, sticky=tk.W)
        ttk.Label(frame, text="Host:").grid(column=1, row=4, sticky=tk.W)
        ttk.Label(frame, text="SSH key:").grid(column=1, row=5, sticky=tk.W)
        ttk.Label(frame, text="SSH config:").grid(column=1, row=6, sticky=tk.W)
        ttk.Label(frame, text="SSH config host:").grid(column=1, row=7, sticky=tk.W)

        btn_ssh_key = ttk.Button(
            frame,
            text="Search SSH Key",
            command=lambda: self._open_file(self.ssh_key),
        )
        btn_ssh_key.grid(column=3, row=5, sticky="we")

        btn_ssh_config = ttk.Button(
            frame,
            text="Search SSH config",
            command=lambda: self._open_file(self.ssh_config),
        )
        btn_ssh_config.grid(column=3, row=6, sticky="we")

        ttk.Button(frame, text="Connect", command=self._do_connect).grid(
            column=1, row=9, sticky=tk.W
        )

        self.widgets_conn_user = (
            txt_user,
            txt_password,
            txt_host,
        )
        self.widgets_conn_ssh_key = (
            txt_user,
            txt_host,
            txt_ssh_key,
            btn_ssh_key,
        )
        self.widgets_conn_ssh_host = (
            txt_ssh_config,
            txt_ssh_config_host,
            btn_ssh_config,
        )

        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def _create_remote_user_frame(self, frame: ttk.Frame) -> None:
        ttk.Label(frame, text="Username:").grid(column=1, row=1, sticky=tk.E)

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
        menu_remote = tk.Menu(menubar)

        menubar.add_cascade(menu=menu_file, label="File", underline=0)
        menubar.add_cascade(menu=menu_conn, label="Connection", underline=1)
        menubar.add_cascade(menu=menu_remote, label="Remote platform", underline=0)

        menu_file.add_command(label="Exit", command=self._exit_app)

        menu_conn.add_command(label="User", command=lambda: self.set_conn_type("User"))
        menu_conn.add_command(
            label="SSH Key", command=lambda: self.set_conn_type("SSH key")
        )
        menu_conn.add_command(
            label="SSH Host", command=lambda: self.set_conn_type("SSH host")
        )

        menu_remote.add_command(label="User")
        menu_remote.add_command(label="Packages")

    def _exit_app(self) -> None:
        """Exit from the app"""
        self.ssh_conn.close()
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

    def get_txt_values(self) -> dict:
        """Fill the txt fields with config values"""

        txt_values: dict = {}

        txt_values["user"] = self.user.get()
        txt_values["password"] = self.password.get()
        txt_values["host"] = self.host.get()
        txt_values["ssh_key"] = self.ssh_key.get()
        txt_values["ssh_config"] = self.ssh_config.get()
        txt_values["ssh_config_host"] = self.ssh_config_host.get()
        txt_values["connection_type"] = self.connection_type.get()

        return txt_values

    def set_conn_type(self, conn_type: str) -> None:
        """Set the GUI to the conn_type"""

        widget: Optional[Widget] = None

        for widget in self.widgets_conn_user:
            widget.config(state="disabled")
        for widget in self.widgets_conn_ssh_key:
            widget.config(state="disabled")
        for widget in self.widgets_conn_ssh_host:
            widget.config(state="disabled")

        self.connection_type.set(conn_type)

        if conn_type == "SSH key":
            for widget in self.widgets_conn_ssh_key:
                widget.config(state="normal")
        elif conn_type == "SSH host":
            for widget in self.widgets_conn_ssh_host:
                widget.config(state="normal")
        else:
            # If none of above then use user
            self.connection_type.set("User")
            for widget in self.widgets_conn_user:
                widget.config(state="normal")

    def _do_connect(self) -> None:
        """Do SSH conection"""

        error_msg = self.ssh_conn.connect(self.get_txt_values())

        if error_msg:
            messagebox.showerror("Connection error", error_msg)
            return

        app_config.set_conn_config(self.get_txt_values())
