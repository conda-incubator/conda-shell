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
        prompt = environ.get("prompt", "")
        current_prompt_modifier = environ.get("CONDA_PROMPT_MODIFIER")
        if current_prompt_modifier:
            prompt = re.sub(re.escape(current_prompt_modifier), r"", prompt)
        set_vars.update(
            {
                "prompt": conda_prompt_modifier + prompt,
            }
        )

@hookimpl
def conda_shells():
    yield CondaShellPlugins(
        name="csh_cl",
        summary="Plugin for csh and tcsh used for activate, deactivate, and reactivate",
        osexec=False,
        custom=None,
        script_path=None,
        pathsep_join=":".join,
        sep="/",
        path_conversion=native_path_to_unix,
        script_extension=".csh",
        tempfile_extension=None,
        command_join=";\n",
        run_script_tmpl='source "%s"',
        unset_var_tmpl="unsetenv %s",
        export_var_tmpl="setenv %s '%s'",
        set_var_tmpl="set %s='%s'",
        define_update_prompt=staticmethod(Up._update_prompt),
    )
