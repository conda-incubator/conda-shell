# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import re
import os

from conda.activate import native_path_to_unix
from condact import CondaShellPlugins, hookimpl

class Up:
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

@hookimpl
def conda_shells():
    yield CondaShellPlugins(
        name="posix_cl",
        summary="Plugin for POSIX shells used for activate, deactivate, and reactivate",
        osexec=False,
        script_path=os.path.abspath("posix_ose.py"),
        pathsep_join=":".join,
        sep="/",
        path_conversion=native_path_to_unix,
        script_extension=".sh",
        tempfile_extension=None,
        command_join="\n",
        run_script_tmpl='. "%s"',
        unset_var_tmpl="unset %s",
        export_var_tmpl="export %s='%s'",
        set_var_tmpl="%s='%s'",
        define_update_prompt=staticmethod(Up._update_prompt),
    )
