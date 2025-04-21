# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main GUI kaajal modulefile"""

import logging

from kaajal.config import app_config
from kaajal.gui.mainwindow import MainWindow

logger = logging.getLogger(__name__)


def kaajalw(standalone: bool = True) -> int:
    """Main function to use the GUI"""

    if standalone:
        app_config.load_conn_config()
        app_config.load_log_config()

    try:
        main_window = MainWindow()
        main_window.iconify()
        main_window.set_conn_type(app_config.get_conn_type())
        main_window.fill_txt_values(app_config.conn_config)
        main_window.update()
        main_window.deiconify()
        # iconify, update and deiconify: used to window pops up on top on Windows
        main_window.mainloop()
    # TODO: Test this on a no GUI environment
    except Exception:
        logger.exception("Internal launch or mainloop error")
    else:
        app_config.save_conn_config()
        app_config.save_log_config()

    return 0
