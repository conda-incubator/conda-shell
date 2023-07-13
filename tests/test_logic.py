from argparse import Namespace
from collections import namedtuple
import inspect
from pathlib import PurePath
import os
import pytest

from condact.logic import PluginActivator, _ActivatorChild

@pytest.mark.osexec
def test_osexec_init_happy_path(plugin_hook):
    """
    Test that the properties of the initialized PluginActivator instance correspond
    to the properties of the passed in plugin hook.
    """
    activator = PluginActivator(plugin_hook)

    assert activator.name == "shellplugin"
    assert activator.summary == "test plugin"
    assert activator.osexec == True
    assert activator.script_path == "abc.sh"
    assert activator.pathsep_join(["a", "b", "c"]) == "a:b:c"
    assert activator.sep == "/"
    assert activator.path_conversion(1) == 2
    assert activator.script_extension == ".sh"
    assert activator.tempfile_extension == None
    assert activator.command_join == "\n"
    assert activator.run_script_tmpl % "hello" == '. "hello"'
    assert activator.unset_var_tmpl % "hello" == "unset hello"
    assert activator.export_var_tmpl % ("hello", "hola") == "export hello='hola'"
    assert activator.set_var_tmpl % ("hello", "hola") == "hello='hola'"
    assert activator.define_update_prompt(1) == "hey, 1"
    assert activator.environ

@pytest.mark.osexec
def test_osexec_init_missing_fields_assigned_None():
    """
    Test that a named tuple that does not include all the properties of the shell hook specification
    initializes a PluginActivator instance that contains all the expected properties,
    with properties missing from the named tuple are assigned ``None``."""
    Syntax = namedtuple("empty_plugin", "name, summary")
    activator = PluginActivator(Syntax("empty_plugin", "plugin with missing fields"))

    assert activator.name == "empty_plugin"
    assert activator.summary == "plugin with missing fields"
    assert activator.script_path is None
    assert activator.pathsep_join is None
    assert activator.sep is None
    assert activator.path_conversion is None
    assert activator.script_extension is None
    assert activator.tempfile_extension is None
    assert activator.command_join is None
    assert activator.run_script_tmpl is None
    assert activator.environ


EMPTY_CMDS_DICT = {
    "unset_vars": [],
    "set_vars": {},
    "export_path": {},
    "export_vars": {},
}

@pytest.mark.osexec
def test_osexec_update_env_map_empty_cmd_dict_no_change(plugin_hook):
    """
    Test that the environment mapping is not changed when the cmd_dict is empty.
    """
    current_env = os.environ.copy()

    activator = PluginActivator(plugin_hook)
    env_map = activator.update_env_map(EMPTY_CMDS_DICT)

    assert env_map == current_env


CMDS_DICT_UNSET_SET_ONLY = {
    "unset_vars": ["FRIES", "CHIPS"],
    "set_vars": {"HIGHWAY": "freeway"},
}

@pytest.mark.osexec
def test_osexec_update_env_map_unset_set_only(plugin_hook, monkeypatch):
    """
    Test that new environment mapping is updated correctly with cmd_dict that only contains
    unset_vars and set_vars keys.
    """
    current_env = os.environ.copy()
    current_env.update({"HIGHWAY": "freeway"})

    # activator makes its own copy of os.environ, so we need to update env vars directly
    monkeypatch.setenv("FRIES", "with ketchup")
    monkeypatch.setenv("CHIPS", "with vinegar")

    activator = PluginActivator(plugin_hook)
    env_map = activator.update_env_map(CMDS_DICT_UNSET_SET_ONLY)

    assert env_map.get("FRIES", None) is None
    assert env_map.get("CHIPS", None) is None
    assert env_map["HIGHWAY"] == "freeway"
    assert env_map == current_env

@pytest.mark.osexec
def test_osexec_update_env_map_missing_env_var(plugin_hook, monkeypatch):
    """
    Test that new environment mapping is updated correctly with cmd_dict that contains
    an unset var that does not exist in the current environment.
    """
    current_env = os.environ.copy()
    current_env.update({"HIGHWAY": "freeway"})

    # activator makes its own copy of os.environ, so we need to update env vars directly
    monkeypatch.setenv("CHIPS", "with vinegar")

    activator = PluginActivator(plugin_hook)
    env_map = activator.update_env_map(CMDS_DICT_UNSET_SET_ONLY)

    assert env_map.get("FRIES", None) is None
    assert env_map.get("CHIPS", None) is None
    assert env_map["HIGHWAY"] == "freeway"
    assert env_map == current_env


# use data types that need to be converted to strings
CMDS_DICT_ALL = {
    "unset_vars": ["A", 1],
    "set_vars": {"B": 2, "C": "c", 4: True},
    "export_path": {"PATH": "/".join([".", "a", "b", "c"])},
    "export_vars": {"E": 5, "F": "f", 6: False},
}

@pytest.mark.osexec
def test_osexec_update_env_map_all(plugin_hook, monkeypatch):
    """
    Test that new environment mapping is updated correctly with cmd_dict that contains
    variables to be set, unset, and exported.
    """
    combined_dict = {
        **CMDS_DICT_ALL["set_vars"],
        **CMDS_DICT_ALL["export_path"],
        **CMDS_DICT_ALL["export_vars"],
    }
    update_dict = {str(k): str(v) for k, v in combined_dict.items()}
    current_env = os.environ.copy()
    current_env.update(update_dict)

    # activator makes its own copy of os.environ, so we need to update env vars directly
    monkeypatch.setenv("A", "a")
    monkeypatch.setenv("1", "one")

    activator = PluginActivator(plugin_hook)
    env_map = activator.update_env_map(CMDS_DICT_ALL)

    assert env_map.get("A", None) is None
    assert env_map.get("1", None) is None
    assert env_map["B"] == "2"
    assert env_map["C"] == "c"
    assert env_map["4"] == "True"
    assert env_map["PATH"] == "./a/b/c"
    assert env_map["E"] == "5"
    assert env_map["F"] == "f"
    assert env_map["6"] == "False"
    assert env_map == current_env

@pytest.mark.osexec
def test_osexec_parse_and_build_cl_activate_cmd_dict(posix_ose_hook):
    """
    Test that a namespace used to activate the base environment with an os.exec* hook
    returns a command dictionary with the expected keys and values.
    """
    ns = Namespace(command="activate", env=None, dev=False, stack=None)
    activator = PluginActivator(posix_ose_hook)
    builder = activator.parse_and_build(ns)
    print(builder["export_vars"])

    # only export vars are CONDA_SHLVL and PATH
    assert isinstance(builder["unset_vars"], tuple)
    assert isinstance(builder["set_vars"], dict)
    assert isinstance(builder["export_vars"], dict)
    assert int(builder["export_vars"]["CONDA_SHLVL"]) == 1
    assert "/" in builder["export_vars"]["PATH"]

@pytest.mark.currentlogic
def test_cl_init_happy_path(posix_cl_hook):
    """
    Test that the properties of the initialized PluginActivator instance correspond
    to the properties of the passed in plugin hook.
    """
    ns = Namespace(command="activate", env=None, dev=False, stack=None)
    activator = _ActivatorChild(posix_cl_hook, ns)

    assert activator.name == "posix_cl"
    assert activator.summary == "Plugin for POSIX shells used for activate, deactivate, and reactivate"
    assert activator.osexec == False
    assert PurePath(activator.script_path).name == "posix_ose.py"
    assert activator.pathsep_join(["a", "b", "c"]) == "a:b:c"
    assert activator.sep == "/"
    assert inspect.isfunction(activator.path_conversion)
    assert activator.script_extension == ".sh"
    assert activator.tempfile_extension == None
    assert activator.command_join == "\n"
    assert activator.run_script_tmpl % "hello" == '. "hello"'
    assert activator.unset_var_tmpl % "hello" == "unset hello"
    assert activator.export_var_tmpl % ("hello", "hola") == "export hello='hola'"
    assert activator.set_var_tmpl % ("hello", "hola") == "hello='hola'"
    assert "Update setvars dict" in inspect.getdoc(activator.define_update_prompt)
    assert activator._raw_arguments == ns
    assert activator.environ


@pytest.mark.currentlogic
def test_update_prompt_no_current_prompt_modifier(posix_cl_hook,  monkeypatch):
    """
    Test that the correct prompt modifier is added to set_vars when there is no current
    prompt modifier.
    """
    monkeypatch.setenv("CONDA_PROMPT_MODIFIER", None)
    monkeypatch.setenv("PS1", "darkness, my old friend")
    ns = Namespace(command="activate", env=None, dev=False, stack=None)
    set_vars = {}

    activator = _ActivatorChild(posix_cl_hook, ns)
    activator._update_prompt(set_vars, "(hello) ")

    assert set_vars["PS1"] == "(hello) darkness, my old friend"