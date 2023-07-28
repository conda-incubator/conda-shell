# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import os
import re

from conda.activate import native_path_to_unix

from condact import CondaShellPlugins, hookimpl
from condact.logic import PluginActivator

class Custom:
    def _update_prompt(environ: os.environ, set_vars: dict, conda_prompt_modifier: str) -> None:
        """
        Update setvars dict with a key and value used to update the shell prompt.
        The new setvars key is the environment variable used to update the shell prompt.
        The new setvars value is the prompt to be displayed following environment activation.
        The logic of this function was copied from conda/activate.py:PosixActivator._update_prompt.
        """
        ps1 = environ.get("PS1", "")
        if "POWERLINE_COMMAND" in ps1:
            # Defer to powerline (https://github.com/powerline/powerline) if it's in use.
            return
        current_prompt_modifier = environ.get("CONDA_PROMPT_MODIFIER")
        if current_prompt_modifier:
            ps1 = re.sub(re.escape(current_prompt_modifier), r"", ps1)
        # Because we're using single-quotes to set shell variables, we need to handle the
        # proper escaping of single quotes that are already part of the string.
        # Best solution appears to be https://stackoverflow.com/a/1250279
        ps1 = ps1.replace("'", "'\"'\"'")
        set_vars.update(
            {
                "PS1": conda_prompt_modifier + ps1,
            }
        )

def write_script(script_path: str, argv: list) -> None:
    with open(script_path, "w") as script_file:
            script_file.write("#!/bin/sh \n")
            for a in argv:
                script_file.write(a+"\n")
            # script_file.write("PS1=$CONDA_PROMPT_MODIFIER+$PS1 \n")

def custom_activate(activator: PluginActivator, cmds_dict: dict) -> SystemExit:
    path = "/bin/bash"
    env_args = activator._get_env_arg_list(cmds_dict, [])
    write_script(activator.script_path, env_args)

    os.execv(path, [path, "--rcfile", activator.script_path])

@hookimpl
def conda_shells():
    yield CondaShellPlugins(
        name="bash_ose",
        summary="Plugin for Bash used for activate, deactivate, and reactivate",
        osexec=True,
        custom=custom_activate,
        script_path=os.path.abspath("condact/scripts/bash_ose.sh"),
        pathsep_join=":".join,
        sep=os.sep,
        path_conversion=native_path_to_unix,
        script_extension=".sh",
        tempfile_extension=None,
        command_join="\n",
        run_script_tmpl='. "%s"',
        unset_var_tmpl="unset %s",
        export_var_tmpl="export %s='%s'",
        set_var_tmpl="%s='%s'",
        define_update_prompt=staticmethod(Custom._update_prompt),
    )
