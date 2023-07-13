import pytest

from conda.plugins.hookspec import CondaSpecs
from conda.plugins.manager import CondaPluginManager
from condact.shell_hookspec import hookimpl, ShellPluginSpecs

from condact.shell_types import CondaShellPlugins

@pytest.fixture
def plugin_manager(mocker):
    pm = CondaPluginManager()
    pm.add_hookspecs(CondaSpecs)
    mocker.patch("conda.plugins.manager.get_plugin_manager", return_value=pm)
    pm.add_hookspecs(ShellPluginSpecs)
    pm.load_plugins("shells")
    pm.load_entrypoints("conda")
    mocker.patch("condact.shell_manager.update_plugin_manager", return_value=pm)
    return pm