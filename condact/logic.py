# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import argparse
import os
from typing import NamedTuple

from conda.activate import _Activator
from conda.base.context import context

from .shell_types import CondaShellPlugins

class PluginActivator:
    """
    Activate and deactivate have two tasks:
        1. Set and unset environment variables
        2. Execute/source activate.d/deactivate.d scripts

    Shells should also use 'reactivate' following conda's install, update, and
        remove/uninstall commands.

    All core logic is in build_activate() or build_deactivate(), and is independent of
    shell type.  Each returns a map containing the keys:
        export_vars
        unset_var
        activate_scripts
        deactivate_scripts

    Each shell plugin hook provides the shell-specific information needed to implement
    the methods of this class.
    """

    def __init__(self, syntax: NamedTuple):
        """
        Create properties so that each class property is assigned the value from the corresponding
        property in the named tuple, based on the expected fields in the shell plugin hook.
        If a property is missing from the named tuple, it will be assigned a value of None.

        Expected properties:
            self.name: str
            self.summary: str
            self.osexec: bool
            script_path: str
            self.pathsep_join: str
            self.sep: str
            self.path_conversion: Callable[
                [str | Iterable[str] | None], str | tuple[str, ...] | None
            ]
            self.script_extension: str
            self.tempfile_extension: str | None
            self.command_join: str
            self.run_script_tmpl: str
            self.unset_var_tmpl: str | None
            self.export_var_tmpl: str | None
            self.set_var_tmpl: str | None
            self.define_update_prompt: Callable[[dict, str], None] | None
            self.environ: mapping
            self._activator: _Activator

        """
        for field in CondaShellPlugins._fields:
            setattr(self, field, getattr(syntax, field, None))

        self.environ = os.environ.copy()

        # initializing an instance of _Activator just so that we can use some of its
        # methods rather than duplicating code
        self._activator = _ActivatorChild(syntax, [])

    def update_env_map(self, cmds_dict: dict) -> map:
        """
        Create an environment mapping for use with os.execve, based on the builder dictionary.
        """
        env_map = os.environ.copy()

        unset_vars = cmds_dict["unset_vars"]
        set_vars = cmds_dict["set_vars"]
        export_path = cmds_dict.get("export_path", {})
        export_vars = cmds_dict.get("export_vars", {})

        for key in unset_vars:
            env_map.pop(str(key), None)

        for key, value in set_vars.items():
            env_map[str(key)] = str(value)

        for key, value in export_path.items():
            env_map[str(key)] = str(value)

        for key, value in export_vars.items():
            env_map[str(key)] = str(value)

        return env_map

    def get_activate_builder(self) -> dict:
        """
        Create dictionary containing the environment variables to be set, unset and
        exported, as well as the package activation and deactivation scripts to be run.
        """
        if self.stack:
            builder_result = self._build_activate_stack(self.env_name_or_prefix, True)
        else:
            builder_result = self._build_activate_stack(self.env_name_or_prefix, False)
        return builder_result

    def parse_and_build(self, args: argparse.Namespace) -> dict:
        """
        Parse CLI arguments. Build and return the dictionary that contains environment variables
            to be set, unset, and exported, and any relevant package activation and deactivation
            scripts that should be run.
        Set context.dev if a --dev flag exists.
        For activate, set self.env_name_or_prefix and self.stack.
        """
        context.dev = args.dev or context.dev

        # run _ActivatorChild._parse_and_set_args() to set self.command, context.dev,
        # self.env_name_or_prefix and self.stack for other _Activator methods
        self._activator._parse_and_set_args(args)

        if args.command == "activate":
            self.env_name_or_prefix = args.env or "base"
            if args.stack is None:
                self.stack = context.auto_stack and context.shlvl <= context.auto_stack
            else:
                self.stack = args.stack
            cmds_dict = self.get_activate_builder()
        elif args.command == "deactivate":
            cmds_dict = self.build_deactivate()
        elif args.command == "reactivate":
            cmds_dict = self.build_reactivate()

        return cmds_dict
    
    def activate(self, cmds_dict: dict) -> SystemExit:
        """
        Change environment. As a new process in in new environment, run deactivate
        scripts from packages in old environment (to reset env variables) and
        activate scripts from packages installed in new environment.
        """
        path = self.script_path
        arg_list = [path]
        env_map = self.update_env_map(cmds_dict)

        deactivate_scripts = cmds_dict.get("deactivate_scripts", ())

        if deactivate_scripts:
            deactivate_list = [
                (self.run_script_tmpl % script) + self.command_join
                for script in deactivate_scripts
            ]
            arg_list.extend(deactivate_list)

        activate_scripts = cmds_dict.get("activate_scripts", ())

        if activate_scripts:
            activate_list = [
                (self.run_script_tmpl % script) + self.command_join
                for script in activate_scripts
            ]
            arg_list.extend(activate_list)

        os.execve(path, arg_list, env_map)

    def _build_activate_stack(self, env_name_or_prefix: str, stack: bool) -> dict:
        """
        Build dictionary with the following key-value pairs, to be used in creating the new
        environment to be activated:
            unset_vars: list containing environmental variables to be unset
            set_vars: dictionary containing environmental variables to be set, as key-value pairs
            export_vars: dictionary containing environmental variables to be exported, as
                key-value pairs
            deactivate_scripts: tuple containing scripts associated with installed packages
                that should be run on deactivation (from `deactivate.d`), if any
            activate_scripts: tuple containing scripts associated with installed packages
                that should be run on activation (from `activate.d`), if any
        """
        return self._activator._build_activate_stack(env_name_or_prefix, stack)
    
    def build_deactivate(self) -> dict:
        """
        Build dictionary with the following key-value pairs, to be used in creating the new
        environment to be activated (that is, the previous environment used):
            unset_vars: list containing environmental variables to be unset
            set_vars: dictionary containing environmental variables to be set, as key-value pairs
            export_vars: dictionary containing environmental variables to be exported, as
                key-value pairs
            deactivate_scripts: tuple containing scripts associated with installed packages
                that should be run on deactivation (from `deactivate.d`), if any
            activate_scripts: tuple containing scripts associated with installed packages
                that should be run on activation (from `activate.d`), if any
        """
        return self._activator.build_deactivate()
    
    def build_reactivate(self) -> dict:
        """
        Build dictionary with the following key-value pairs, to be used in updating the
        environment mapping:
            unset_vars: list containing environmental variables to be unset
            set_vars: dictionary containing environmental variables to be set, as key-value pairs
            export_vars: dictionary containing environmental variables to be exported, as
                key-value pairs
            deactivate_scripts: tuple containing scripts associated with installed packages
                that should be run on deactivation (from `deactivate.d`), if any
            activate_scripts: tuple containing scripts associated with installed packages
                that should be run on activation (from `activate.d`), if any
        """
        return self._activator.build_reactivate()


class _ActivatorChild(_Activator):
    """"
    Consume shell hook to create child class compatible with the current conda activator logic.
    This class does not contain any public methods.
    """
    def __init__(self, syntax: NamedTuple, arguments: argparse.Namespace | list[str]):
        """
        Create properties so that each class property is assigned the value from the corresponding
        property in the named tuple, based on the expected fields in the shell plugin hook.
        If a property is missing from the named tuple, it will be assigned a value of None.

        Expected properties:
            self.name: str
            self.summary: str
            self.osexec: bool
            script_path: str
            self.pathsep_join: str
            self.sep: str
            self.path_conversion: Callable[
                [str | Iterable[str] | None], str | tuple[str, ...] | None
            ]
            self.script_extension: str
            self.tempfile_extension: str | None
            self.command_join: str
            self.run_script_tmpl: str
            self.unset_var_tmpl: str | None
            self.export_var_tmpl: str | None
            self.set_var_tmpl: str | None
            self.define_update_prompt: Callable[[dict, str], None] | None
            
            From _Activator:
                self._raw_arguments: argparse.Namespace | list[str]
                self.environ: mapping

        """

        for field in CondaShellPlugins._fields:
            setattr(self, field, getattr(syntax, field, None))

        self.hook_source_path = ""
        return super().__init__(arguments)

    def _update_prompt(self, set_vars: dict, conda_prompt_modifier: str) -> None:
        """
        Update the prompt to include the current environment.

        Parameters
        ----------
        set_vars : dict
            Dictionary of environment variables to set.
        conda_prompt_modifier :
            String to append to the prompt.
        """
        if self.define_update_prompt:
            return self.define_update_prompt(environ=self.environ, set_vars=set_vars, conda_prompt_modifier=conda_prompt_modifier)
        else:
            pass

    def _hook_preamble(self) -> str:
        """Placeholder function. ``_Activator`` requires child classes to include this method."""
        return ""
    
    def _parse_and_set_args(self, args: argparse.Namespace) -> None:
        """
        Set self.command to the specified command (activate, deactivate, reactivate).
        Set context.dev if a --dev flag exists.
        For activate, set self.env_name_or_prefix and self.stack.
        """
        self.command = args.command
        context.dev = args.dev or context.dev

        if self.command == "activate":
            self.env_name_or_prefix = args.env or "base"

            if args.stack is None:
                self.stack = context.auto_stack and context.shlvl <= context.auto_stack
            else:
                self.stack = args.stack

        return