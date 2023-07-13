# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import pytest

from conda.exceptions import PluginError
from conda.plugins.hookspec import CondaSpecs
from conda.plugins.manager import CondaPluginManager
from conda.base.context import context


from condact.shell_hookspec import hookimpl, ShellPluginSpecs
from condact.shell_manager import get_shell_syntax
from condact.shell_types import CondaShellPlugins

class BashPlugin:
    @hookimpl
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
            define_update_prompt=lambda x: f"hey, {str(x)}",
        )


class OtherPlugin:
    @hookimpl
    def conda_shells():
        yield CondaShellPlugins(
            name="shellplugin2",
            summary="second test plugin",
            osexec=False,
            script_path="xyz.fish",
            pathsep_join=":".join,
            sep="/",
            path_conversion=lambda x: x+4,
            script_extension=".fish",
            tempfile_extension=".tmp",
            command_join=";\n",
            run_script_tmpl='. "%s"',
            unset_var_tmpl="unset %s",
            export_var_tmpl="export %s='%s'",
            set_var_tmpl="%s='%s'",
            define_update_prompt=lambda x: str(x),
        )


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
    syntax = get_shell_syntax(plugin_manager, "shellplugin")

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
    assert getattr(syntax, "define_update_prompt", None)(1) == "hey, 1"


def test_get_shell_syntax_multiple_plugins(plugin_manager):
    """Ensure correct shell hook is returned if multiple plugins are yielded."""
    plugin_manager.load_plugins(BashPlugin, OtherPlugin)

    syntax = get_shell_syntax(plugin_manager, "shellplugin2")

    assert getattr(syntax, "name", None) == "shellplugin2"
    assert getattr(syntax, "summary", None) == "second test plugin"
    assert getattr(syntax, "osexec", None) == False
    assert getattr(syntax, "script_path", None) == "xyz.fish"
    assert getattr(syntax, "pathsep_join", None)(["a", "b", "c"]) == "a:b:c"
    assert getattr(syntax, "sep", None) == "/"
    assert getattr(syntax, "path_conversion", None)(1) == 5
    assert getattr(syntax, "script_extension", None) == ".fish"
    assert getattr(syntax, "tempfile_extension", True) == ".tmp"
    assert getattr(syntax, "command_join", None) == ";\n"
    assert getattr(syntax, "run_script_tmpl", None) % "hello" == '. "hello"'
    assert getattr(syntax, "unset_var_tmpl", None) % "hello" == "unset hello"
    assert getattr(syntax, "export_var_tmpl", None) % ("hello", "hola") == "export hello='hola'"
    assert getattr(syntax, "set_var_tmpl", None) % ("hello", "hola") == "hello='hola'"
    assert getattr(syntax, "define_update_prompt", None)(1) == "1"


def test_get_shell_syntax_error_no_plugins(plugin_manager):
    """Raise error if no shell plugins are yielded."""
    plugin_manager.load_plugins()

    with pytest.raises(PluginError) as e:
        get_shell_syntax(plugin_manager, "BashPlugin")

    assert "No shell plugins found" in str(e.value)


def test_get_shell_syntax_error_wrong_plugin(plugin_manager):
    """Raise error if no shell plugins are yielded."""
    plugin_manager.load_plugins(BashPlugin, OtherPlugin)

    with pytest.raises(PluginError) as e:
        get_shell_syntax(plugin_manager, "FunPlugin")

    assert "No shell plugin found" in str(e.value)
    assert "FunPlugin" in str(e.value)