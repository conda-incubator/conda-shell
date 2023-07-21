import pytest
import uuid

from typing import Iterable, NamedTuple

from conda.plugins.hookspec import CondaSpecs
from conda.plugins.manager import CondaPluginManager
from conda.testing import conda_cli
from condact.shell_hookspec import ShellPluginSpecs
from condact.shell_manager import get_shell_syntax
from condact.plugins import posix_cl, posix_ose

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


@pytest.fixture
def posix_ose_hook(plugin_manager) -> NamedTuple:
    """Return the POSIX os.exec* plugin hook with the name 'posix_ose'."""
    pm = plugin_manager
    pm.load_plugins(posix_ose)
    return get_shell_syntax(pm, "posix_ose")


@pytest.fixture
def posix_cl_hook(plugin_manager) -> NamedTuple:
    """Return the POSIX os.exec* plugin hook with the name 'posix_ose'."""
    pm = plugin_manager
    pm.load_plugins(posix_cl)
    return get_shell_syntax(pm, "posix_cl")


@pytest.fixture
def temp_env(conda_cli: conda_cli) -> Iterable[str]:
    """Create environment with no packages"""
    # Setup
    name = uuid.uuid4().hex
    conda_cli("create", "--name", name, "--yes")

    yield name

    # Teardown
    conda_cli("remove", "--all", "--yes", "--name", name)