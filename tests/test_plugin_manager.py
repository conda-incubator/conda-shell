# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import pytest
from pytest_mock import mocker

from conda.exceptions import PluginError
from conda.plugins.hookspec import CondaSpecs
from conda.plugins.manager import CondaPluginManager
from conda.base.context import context


import plugin_manager
from plugin_manager.shell_hookspec import ShellPluginSpecs
from plugin_manager.shell_manager import get_shell_syntax
from plugin_manager.shell_types import CondaShellPlugins

class BashPlugin:
    @plugin_manager.hookimpl
    def conda_shells():
        yield CondaShellPlugins(
            name="shellplugin",
            summary="test plugin",
            osexec=True,
            script_path="abc.sh",
            pathsep_join=":".join,
            sep="/",
            path_conversion=lambda x: x + 1,
            script_extension=".sh",
            tempfile_extension=None,
            command_join="\n",
            run_script_tmpl='. "%s"',
            unset_var_tmpl="unset %s",
            export_var_tmpl="export %s='%s'",
            set_var_tmpl="%s='%s'",
        )


class TwoShellPlugins:
    @plugin_manager.hookimpl
    def conda_shells():
        yield CondaShellPlugins(
            name="shellplugin",
            summary="test plugin",
            osexec=True,
            script_path="abc.sh",
            pathsep_join=":".join,
            sep="/",
            path_conversion=lambda x: x,
            script_extension=".sh",
            tempfile_extension=None,
            command_join="\n",
            run_script_tmpl='. "%s"',
            unset_var_tmpl="unset %s",
            export_var_tmpl="export %s='%s'",
            set_var_tmpl="%s='%s'",
        )
        yield CondaShellPlugins(
            name="shellplugin2",
            summary="second test plugin",
            osexec=False,
            script_path="abc.sh",
            pathsep_join=":".join,
            sep="/",
            path_conversion=lambda x: x,
            script_extension=".sh",
            tempfile_extension=None,
            command_join="\n",
            run_script_tmpl='. "%s"',
            unset_var_tmpl="unset %s",
            export_var_tmpl="export %s='%s'",
            set_var_tmpl="%s='%s'",
        )


@pytest.fixture
def plugin_manager(mocker):
    pm = CondaPluginManager()
    pm.add_hookspecs(CondaSpecs)
    mocker.patch("conda.plugins.manager.get_plugin_manager", return_value=pm)
    pm.add_hookspecs(ShellPluginSpecs)
    pm.load_plugins("shells")
    pm.load_entrypoints("conda")
    mocker.patch("plugin_manager.shell_manager.update_plugin_manager", return_value=pm)
    return pm


def test_load_no_plugins(plugin_manager):
    """Ensure that no plugins are loaded if none are available."""
    plugin_names = plugin_manager.load_plugins()
    assert plugin_names == []


def test_load_shell_plugin(plugin_manager):
    """Ensure that the shell plugin is loaded correctly."""
    pm = plugin_manager
    plugin_names = pm.load_plugins(BashPlugin)
    assert plugin_names == ["BashPlugin"]


def test_get_shell_syntax_happy_path(plugin_manager):
    """Ensure that the shell hook is returned correctly."""
    plugin_manager.load_plugins(BashPlugin)
    syntax = get_shell_syntax(plugin_manager)

    assert getattr(syntax, "name", None) == "shellplugin"
    assert getattr(syntax, "summary", None) == "test plugin"
    assert getattr(syntax, "osexec", None) == True
    assert getattr(syntax, "script_path", None) == "abc.sh"
    assert getattr(syntax, "pathsep_join", None)(["a", "b", "c"]) == "a:b:c"
    assert getattr(syntax, "sep", None) == "/"
    assert getattr(syntax, "path_conversion", None)(1) == 2
    assert getattr(syntax, "script_extension", None) == ".sh"
    assert getattr(syntax, "tempfile_extension", True) == None
    assert getattr(syntax, "command_join", None) == "\n"
    assert getattr(syntax, "run_script_tmpl", None) % "hello" == '. "hello"'
    assert getattr(syntax, "unset_var_tmpl", None) % "hello" == "unset hello"
    assert getattr(syntax, "export_var_tmpl", None) % ("hello", "hola") == "export hello='hola'"
    assert getattr(syntax, "set_var_tmpl", None) % ("hello", "hola") == "hello='hola'"


def test_get_shell_syntax_error_multiple_plugins(plugin_manager):
    """Raise error if multiple shell plugins are yielded."""
    plugin_manager.load_plugins(TwoShellPlugins)

    with pytest.raises(PluginError) as e:
        get_shell_syntax(plugin_manager)

    assert "Multiple compatible plugins found" in str(e.value)
    assert "shellplugin" in str(e.value)
    assert "shellplugin2" in str(e.value)


def test_get_shell_syntax_error_no_plugins(plugin_manager):
    """Raise error if no shell plugins are yielded."""
    plugin_manager.load_plugins()

    with pytest.raises(PluginError) as e:
        get_shell_syntax(plugin_manager)

    assert "No plugins installed are compatible with this shell" in str(e.value)