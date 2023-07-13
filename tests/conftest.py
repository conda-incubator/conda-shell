import pytest

from typing import NamedTuple

from conda.plugins.hookspec import CondaSpecs
from conda.plugins.manager import CondaPluginManager
from condact.shell_hookspec import ShellPluginSpecs
from condact.shell_manager import get_shell_syntax

from .test_manager import BashPlugin

@pytest.fixture
def plugin_manager(mocker) -> CondaPluginManager:
    """Return a mocked plugin manager with the shell hookspec registered but no plugins loaded."""
    pm = CondaPluginManager()
    pm.add_hookspecs(CondaSpecs)
    mocker.patch("conda.plugins.manager.get_plugin_manager", return_value=pm)
    pm.add_hookspecs(ShellPluginSpecs)
    pm.load_entrypoints("conda")
    mocker.patch("condact.shell_manager.update_plugin_manager", return_value=pm)
    return pm

@pytest.fixture
def plugin_hook(plugin_manager) -> NamedTuple:
    """Return the shell plugin hook with the name 'shellplugin'."""
    pm = plugin_manager
    pm.load_plugins(BashPlugin)
    return get_shell_syntax(pm, "shellplugin")