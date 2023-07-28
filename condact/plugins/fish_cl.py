# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import re
import os

from conda.activate import native_path_to_unix
from condact import CondaShellPlugins, hookimpl

@hookimpl
def conda_shells():
    yield CondaShellPlugins(
        name="fish_cl",
        summary="Plugin for fish used for activate, deactivate, and reactivate",
        osexec=False,
        custom=None,
        script_path=None,
        pathsep_join='" "'.join,
        sep="/",
        path_conversion=native_path_to_unix,
        script_extension=".fish",
        tempfile_extension=None,
        command_join=";\n",
        run_script_tmpl='source "%s"',
        unset_var_tmpl ="set -e %s",
        export_var_tmpl='set -gx %s "%s"',
        set_var_tmpl='set -g %s "%s"',
        define_update_prompt=None, # conda init block sets the prompt
    )