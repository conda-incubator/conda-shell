# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from typing import Iterable, Callable

from conda.plugins.manager import (
    CondaPluginManager
)
from conda.base.context import context
from conda.cli.main import init_loggers
from conda.exceptions import PluginError

from .shell_hookspec import ShellPluginSpecs, spec_name

# do I need to cache this?
def update_plugin_manager() -> CondaPluginManager:
    """
    Update the plugin manager with the shell plugin hook.
    Return the updated plugin manager.
    """
    context.__init__()
    init_loggers(context)

    pm = context.plugin_manager
    pm.add_hookspecs(ShellPluginSpecs)
    pm.load_plugins("shells")
    pm.load_entrypoints(spec_name)
    return pm


def get_shell_syntax(pm: CondaPluginManager, plugin_name: str) -> Iterable[Callable]:
    """
    Return shell plugin hook with specified name.
    Raise error if no shell plugin hooks are found.
    """
    shell_hooks = pm.get_hook_results("shells")

    if not shell_hooks:
        raise PluginError("No shell plugins found.")

    for hook in shell_hooks:
        if hook.name == plugin_name:
            return hook
        
    raise PluginError(f"No shell plugin found with name '{plugin_name}'.")