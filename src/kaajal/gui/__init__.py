# c-basic-offset: 4; tab-width: 8; indent-tabs-mode: nil
# vi: set shiftwidth=4 tabstop=8 expandtab:
# :indentSize=4:tabSize=8:noTabs=true:
#
# SPDX-FileCopyrightText: 2025 Intel Corporation
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main GUI kaajal modulefile"""

import logging

from kaajal.gui.mainwindow import MainWindow

logger = logging.getLogger(__name__)


def kaajalw():
    try:
        root = MainWindow()
        root.mainloop()
    # TODO: Test this on a no GUI environment
    except Exception:
        logger.exception("Internal launch or mainloop error")
