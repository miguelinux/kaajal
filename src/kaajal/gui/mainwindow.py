# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main window GUI"""

import logging
import threading
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
from kaajal.distro import Distro

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

        mainframe = ttk.Frame(self)

        notebook = ttk.Notebook(mainframe)
        notebook.pack(expand=True, fill="both")

        conn_frame = ttk.Frame(notebook)
        r_user_frame = ttk.Frame(notebook)
        pkgs_frame = ttk.Frame(notebook)
        repo_frame = ttk.Frame(notebook)
        tb_frame = ttk.Frame(notebook)

        self.connection_type = tk.StringVar()
        self.user = tk.StringVar()
        self.password = tk.StringVar()
        self.host = tk.StringVar()
        self.ssh_key = tk.StringVar()
        self.ssh_config = tk.StringVar()
        self.ssh_config_host = tk.StringVar()
        self.str_status_bar = tk.StringVar()

        # List Remote User String Var
        self.lrusv: list[tk.StringVar] = []

        # String Var of Packages
        self.sv_pkgs = tk.StringVar()
        # Package list file
        self.sv_pkgs_file = tk.StringVar()

        # List of packages
        self.l_pkgs: list[tk.StringVar] = []

        # List of repo data
        self.l_repo: list[tk.StringVar] = []

        # List of tarball
        self.l_tb: list[tk.StringVar] = []

        # Repo Listbox
        self.r_lbox: Optional[tk.Listbox] = None

        # Connection button
        self.btn_conn: ttk.Button

        # Used to create a thread for longest task
        self._working_thread: Optional[threading.Thread] = None

        self._create_conn_frame(conn_frame)
        self._create_remote_user_frame(r_user_frame)
        self._create_packages_frame(pkgs_frame)
        self._create_repo_frame(repo_frame)
        self._create_tarball_frame(tb_frame)

        lbl_status_bar = ttk.Label(mainframe, textvariable=self.str_status_bar)
        lbl_status_bar.configure(relief="sunken", anchor=tk.W)
        lbl_status_bar.pack(fill="x", side="bottom")

        notebook.add(conn_frame, text="Connection")
        notebook.add(r_user_frame, text="User")
        notebook.add(pkgs_frame, text="Packages")
        notebook.add(repo_frame, text="Repos")
        notebook.add(tb_frame, text="Tarballs")
        mainframe.pack(padx=7, pady=7)

        self.ssh_conn = SSHConnection()
        self.distro = Distro()
        self.distro.set_ssh_conn(self.ssh_conn)
        self.str_status_bar.set("Not connected to Linux distro")

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

        self.btn_conn = ttk.Button(frame, text="Connect", command=self._do_connect)
        self.btn_conn.grid(column=1, row=9, sticky=tk.W)

        ttk.Button(frame, text="Distro Update", command=self._distro_update).grid(
            column=2, row=9, sticky=tk.W
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
        ttk.Label(frame, text="Password:").grid(column=1, row=2, sticky=tk.E)
        ttk.Label(frame, text="SSH key:").grid(column=1, row=3, sticky=tk.E)
        ttk.Label(frame, text="GitHub token:").grid(column=1, row=4, sticky=tk.E)

        self.lrusv.append(tk.StringVar())
        txt_ru_u = ttk.Entry(frame, width=15, textvariable=self.lrusv[-1])
        self.lrusv.append(tk.StringVar())
        txt_ru_p = ttk.Entry(frame, width=15, textvariable=self.lrusv[-1])
        self.lrusv.append(tk.StringVar())
        txt_ru_s = ttk.Entry(frame, width=15, textvariable=self.lrusv[-1])
        self.lrusv.append(tk.StringVar())
        txt_ru_t = ttk.Entry(frame, width=15, textvariable=self.lrusv[-1])

        txt_ru_u.grid(column=2, row=1, sticky="we")
        txt_ru_p.grid(column=2, row=2, sticky="we")
        txt_ru_s.grid(column=2, row=3, sticky="we")
        txt_ru_t.grid(column=2, row=4, sticky="we")

        ttk.Button(
            frame,
            text="Search SSH Key",
            command=lambda: self._open_file(self.lrusv[2]),
        ).grid(column=3, row=3, sticky="we")

        ttk.Button(
            frame,
            text="Search GitHub token",
            command=lambda: self._open_file(self.lrusv[3]),
        ).grid(column=3, row=4, sticky="we")

        ttk.Button(frame, text="Create remote user", command=self._create_user).grid(
            column=1, row=5, columnspan=3, sticky="we"
        )
        ttk.Button(frame, text="Copy SSH key to current connected user").grid(
            column=1, row=6, columnspan=3, sticky="we"
        )
        ttk.Button(frame, text="Copy GitHub token to current connected user").grid(
            row=7, column=1, columnspan=3, sticky="we"
        )

        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def _create_packages_frame(self, frame: ttk.Frame) -> None:
        pkg_frame = ttk.LabelFrame(frame, text="Essential packages")
        pkg_frame.grid(row=1, column=1, columnspan=3, sticky="we")

        self.l_pkgs.append(tk.StringVar())
        ttk.Checkbutton(
            pkg_frame, text="git", variable=self.l_pkgs[-1], onvalue="git", offvalue=""
        ).grid(row=1, column=1)

        self.l_pkgs.append(tk.StringVar())
        ttk.Checkbutton(
            pkg_frame,
            text="git-lfs",
            variable=self.l_pkgs[-1],
            onvalue="git-lfs",
            offvalue="",
        ).grid(row=1, column=2)

        self.l_pkgs.append(tk.StringVar())
        ttk.Checkbutton(
            pkg_frame,
            text="tmux",
            variable=self.l_pkgs[-1],
            onvalue="tmux",
            offvalue="",
        ).grid(row=1, column=3)

        self.l_pkgs.append(tk.StringVar())
        ttk.Checkbutton(
            pkg_frame,
            text="python3",
            variable=self.l_pkgs[-1],
            onvalue="python3",
            offvalue="",
        ).grid(row=1, column=4)

        self.l_pkgs.append(tk.StringVar())
        ttk.Checkbutton(
            pkg_frame, text="vim", variable=self.l_pkgs[-1], onvalue="vim", offvalue=""
        ).grid(row=2, column=1)

        self.l_pkgs.append(tk.StringVar())
        ttk.Checkbutton(
            pkg_frame,
            text="rsync",
            variable=self.l_pkgs[-1],
            onvalue="rsync",
            offvalue="",
        ).grid(row=2, column=2)

        self.l_pkgs.append(tk.StringVar())
        ttk.Checkbutton(
            pkg_frame,
            text="curl",
            variable=self.l_pkgs[-1],
            onvalue="curl",
            offvalue="",
        ).grid(row=2, column=3)

        self.l_pkgs.append(tk.StringVar())
        ttk.Checkbutton(
            pkg_frame,
            text="python3-pip",
            variable=self.l_pkgs[-1],
            onvalue="python3-pip",
            offvalue="",
        ).grid(row=2, column=4)

        ttk.Label(frame, text="Packages's list file:").grid(
            row=2, column=1, sticky=tk.E
        )

        txt_p_p = ttk.Entry(frame, width=15, textvariable=self.sv_pkgs_file)
        txt_p_p.grid(row=2, column=2, sticky="we")

        ttk.Button(
            frame,
            text="Search list",
            command=lambda: self._open_file(self.sv_pkgs_file),
        ).grid(row=2, column=3, sticky="we")

        ttk.Label(frame, text="Other packages:").grid(row=3, column=1, sticky=tk.E)

        txt_p_p = ttk.Entry(frame, width=15, textvariable=self.sv_pkgs)
        txt_p_p.grid(row=3, column=2, sticky="we")

        ttk.Button(frame, text="Install packages", command=self._install_pkgs).grid(
            row=4, column=1, sticky="we"
        )

        for child in pkg_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def _create_repo_frame(self, frame: ttk.Frame) -> None:
        ttk.Label(frame, text="Repo URL:").grid(row=1, column=1, sticky=tk.E)
        ttk.Label(frame, text="Path to clone:").grid(row=2, column=1, sticky=tk.E)
        ttk.Label(frame, text="Repo's list file:").grid(row=3, column=1, sticky=tk.E)

        self.l_repo.append(tk.StringVar())
        txt_r_u = ttk.Entry(frame, width=15, textvariable=self.l_repo[-1])
        txt_r_u.grid(row=1, column=2, columnspan=2, sticky="we")

        self.l_repo.append(tk.StringVar())
        txt_r_p = ttk.Entry(frame, width=15, textvariable=self.l_repo[-1])
        txt_r_p.grid(row=2, column=2, columnspan=2, sticky="we")

        self.l_repo.append(tk.StringVar())
        txt_r_f = ttk.Entry(frame, width=15, textvariable=self.l_repo[-1])
        txt_r_f.grid(row=3, column=2, sticky="we")

        ttk.Button(
            frame,
            text="Search list",
            command=lambda: self._open_file(self.l_repo[-1]),
        ).grid(row=3, column=3, sticky="we")

        ttk.Button(
            frame,
            text="Add to List",
            command=self._add_to_repo_list,
        ).grid(row=4, column=3, sticky="we")

        repo_lframe = ttk.LabelFrame(frame, text="List of repos")
        repo_lframe.grid(row=4, column=1, rowspan=3, columnspan=2, sticky="we")

        sbar = ttk.Scrollbar(repo_lframe, orient="horizontal")
        self.r_lbox = tk.Listbox(repo_lframe, height=5, xscrollcommand=sbar.set)
        sbar.config(command=self.r_lbox.xview)

        sbar.pack(side="bottom", fill=tk.X, padx=5, pady=5)
        self.r_lbox.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            frame,
            text="Clone repos",
            command=self._clone_repo,
        ).grid(row=5, column=3, sticky="we")

        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def _create_tarball_frame(self, frame: ttk.Frame) -> None:
        ttk.Label(frame, text="Tarball URL:").grid(row=1, column=1, sticky=tk.E)
        ttk.Label(frame, text="Path to extract:").grid(row=2, column=1, sticky=tk.E)
        ttk.Label(frame, text="Tarball list file:").grid(row=3, column=1, sticky=tk.E)

        self.l_tb.append(tk.StringVar())
        txt_tb_u = ttk.Entry(frame, width=15, textvariable=self.l_tb[-1])
        txt_tb_u.grid(row=1, column=2, columnspan=2, sticky="we")

        self.l_tb.append(tk.StringVar())
        txt_tb_p = ttk.Entry(frame, width=15, textvariable=self.l_tb[-1])
        txt_tb_p.grid(row=2, column=2, columnspan=2, sticky="we")

        self.l_tb.append(tk.StringVar())
        txt_tb_f = ttk.Entry(frame, width=15, textvariable=self.l_tb[-1])
        txt_tb_f.grid(row=3, column=2, sticky="we")

        ttk.Button(
            frame,
            text="Search list",
            command=lambda: self._open_file(self.l_tb[-1]),
        ).grid(row=3, column=3, sticky="we")

        ttk.Button(
            frame,
            text="Install tarball",
            command=self._install_tarball,
        ).grid(row=4, column=1, sticky="we")

        for child in frame.winfo_children():
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

        menu_conn.add_command(label="User", command=lambda: self.set_conn_type("User"))
        menu_conn.add_command(
            label="SSH Key", command=lambda: self.set_conn_type("SSH key")
        )
        menu_conn.add_command(
            label="SSH Host", command=lambda: self.set_conn_type("SSH host")
        )

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

        error_msg = self.distro.identify()

        if error_msg:
            messagebox.showwarning("Linux identifycation warning", error_msg)

        self.btn_conn.config(text="Disconnect", command=self._disconnect)
        self.str_status_bar.set("Connected to " + self.distro.pretty_name)

    def _disconnect(self) -> None:
        """Disconnect from SSH"""

        self.ssh_conn.close()
        self.btn_conn.config(text="Connect", command=self._do_connect)
        self.str_status_bar.set("Not connected to Linux distro")

    def _install_pkgs(self) -> None:
        """Install packages"""

        str_pkg_list = ""
        for sv in self.l_pkgs:
            pkg = sv.get()
            if pkg:
                str_pkg_list += pkg + " "

        pkg = self.sv_pkgs.get()
        if pkg:
            str_pkg_list += pkg

        error_msg = self.distro.install(pkg)

        if error_msg:
            messagebox.showwarning("Linux install warning", error_msg)
            return

    def _add_to_repo_list(self) -> None:
        """Add URL and Path to the list"""

        if self.l_repo[0].get():
            if self.l_repo[1].get():
                repo_path = self.l_repo[0].get() + " " + self.l_repo[1].get()
                if self.r_lbox is not None:
                    self.r_lbox.insert(tk.END, repo_path)

    def _clone_repo(self) -> None:
        """Clone repositories from list"""
        if self.r_lbox is not None:
            items = self.r_lbox.get(0, tk.END)
            print(items)

    def _install_tarball(self) -> None:
        """Install tarball"""

        print("Install tarball")

    def _th_start_distro_update(self) -> None:
        """Function called by the thread"""

        error_msg = self.distro.update()
        self.after(0, self._th_end_distro_update, error_msg)

    def _th_end_distro_update(self, str_msg: str) -> None:
        """Function executed at end of thread"""

        if str_msg:
            messagebox.showwarning("Distro Update Warning", str_msg)
            self.str_status_bar.set("Error when updating distro")
        else:
            self.str_status_bar.set("Linux Distro updated")

        self._working_thread = None

    def _distro_update(self) -> None:
        """Update the Linux distro"""

        if self._working_thread is None:
            self.str_status_bar.set("Updating Linux Distro ... please wait")
            self.update()
            self._working_thread = threading.Thread(target=self._th_start_distro_update)
            self._working_thread.start()
        else:
            error_msg = "Please wait for the background process finish"
            messagebox.showwarning("Distro Update Warning", error_msg)

    def _create_user(self) -> None:
        """Get info to create a user on remote platform"""

        user = self.lrusv[0].get()
        password = self.lrusv[1].get()
        ssh_key = self.lrusv[2].get()
        github_token = self.lrusv[3].get()

        error_msg = self.distro.create_new_user(user, password, ssh_key, github_token)
        if error_msg:
            messagebox.showwarning("Linux create new user warning", error_msg)
            return

        # self.ssh_conn = SSHConnection()
        # self.distro = Distro()
