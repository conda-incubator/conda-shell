# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import logging

import pluggy

from conda import plugins
from conda.plugins.manager import (
    CondaPluginManager,
    get_plugin_manager
)

from .shell_hookspec import ShellPluginSpecs, spec_name
from .shell_types import CondaShellPlugins

# do I need to cache this?
def update_plugin_manager() -> CondaPluginManager:
    """
    Update the plugin manager with the shell plugins.

    :return: The plugin manager.
    """
    pm = get_plugin_manager()
    pm.add_hookspecs(ShellPluginSpecs)
    pm.load_plugins(CondaShellPlugins)
    pm.load_entrypoints(spec_name)
    return pm