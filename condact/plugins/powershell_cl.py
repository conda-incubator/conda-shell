# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import os

from conda.activate import path_identity
from conda.common.compat import on_win
from condact import CondaShellPlugins, hookimpl

@hookimpl
def conda_shells():
    yield CondaShellPlugins(
        name="powershell_cl",
        summary="Plugin for PowerShell used for activate, deactivate, and reactivate",
        osexec=False,
        custom=False,
        script_path=None,
        pathsep_join= ";".join if on_win else ":".join,
        sep="\\" if on_win else "/",
        path_conversion=path_identity,
        script_extension=".ps1",
        tempfile_extension=None,
        command_join="\n",
        run_script_tmpl='. "%s"',
        unset_var_tmpl='$Env:%s = ""',
        export_var_tmpl='$Env:%s = "%s"',
        set_var_tmpl='$Env:%s = "%s"',
        define_update_prompt=None,
    )
