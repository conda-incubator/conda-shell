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
        name="powershell_ose",
        summary="Plugin for PowerShell used for activate, deactivate, and reactivate",
        osexec=True,
        custom=None,
        script_path=os.path.abspath("condact/scripts/ps_ose.ps1"),
        pathsep_join= ";".join if on_win else ":".join,
        sep="\\" if on_win else "/",
        path_conversion=path_identity,
        script_extension=".ps1",
        tempfile_extension=None,
        command_join="\n",
        run_script_tmpl = '. "%s"',
        unset_var_tmpl=None,
        export_var_tmpl=None,
        set_var_tmpl=None,
        define_update_prompt=None,
    )