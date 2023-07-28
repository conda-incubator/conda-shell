# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import os

from conda.activate import native_path_to_unix
from condact import CondaShellPlugins, hookimpl

@hookimpl
def conda_shells():
    yield CondaShellPlugins(
        name="fish_ose",
        summary="Plugin for fish used for activate, deactivate, and reactivate",
        osexec=True,
        custom=False,
        script_path=os.path.abspath("condact/scripts/fish_ose.fish"),
        pathsep_join='" "'.join,
        sep="/",
        path_conversion=native_path_to_unix,
        script_extension=".fish",
        tempfile_extension=None,
        command_join=";\n",
        run_script_tmpl='source "%s"',
        unset_var_tmpl=None,
        export_var_tmpl=None,
        set_var_tmpl=None,
        define_update_prompt=None,
    )
