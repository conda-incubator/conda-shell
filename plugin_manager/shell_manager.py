# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from auxlib.ish import dals
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


def get_shell_syntax(pm: CondaPluginManager) -> CondaPluginManager:
    """
    Return shell plugin hook that is compatible with shell only if one hook is available.
    Raise error if more than one installed plugin yields a hook or if no hooks are yielded.
    """
    shell_hooks = pm.get_hook_results("shells")

    if len(shell_hooks) > 1:
        raise PluginError(
            dals(
                f"""
                Multiple compatible plugins found: please install only one plugin per shell.
                Compatible plugins found:
                {', '.join([plugin.name for plugin in shell_hooks])}"""
            )
        )
    if not shell_hooks:
        raise PluginError("No plugins installed are compatible with this shell.")

    return shell_hooks[0]