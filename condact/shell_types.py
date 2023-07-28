# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from typing import Callable, Iterable, NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from condact.logic import PluginActivator

class CondaShellPlugins(NamedTuple):
    """
    A conda shell plugin.
    If the shell plugin uses os.exec* to activate the environment, the ``osexec`` attribute
    should be set to ``True``. Otherwise, it should be set to ``False``.
    
    All shell plugins must define the following attributes:
    - ``name``
    - ``summary``
    - ``os.exec``
    - ``pathsep_join``
    - ``sep``
    - ``path_conversion``
    - ``script_extension``
    - ``command_join``
    - ``run_script_tmpl``

    If the ``os.exec`` attribute is set to ``True``, ``script_path`` should be set and
    the following attributes should be set to ``None``:
    - ``unset_var_tmpl``
    - ``export_var_tmpl``
    - ``set_var_tmpl``
    - ``tempfile_extension``
    - ``define_update_prompt``
    
    If the ``os.exec`` attribute is set to ``False``, the following attributes must be defined:
    - ``export_var_tmpl``
    - ``unset_var_tmpl``
    - ``set_var_tmpl``

    ``tempfile_extension`` should be set if ``os.exec`` is set to ``False`` and the shell requires
    commands to be read from a temporary file to allow for environment activation.

    :param name: Shell plugin name (e.g., ``posix-plugin``).
    :param summary: Shell plugin summary, will be shown in ``conda --help``.
    :param osexec: Whether the shell plugin uses os.exec* to activate the environment.
    :param custom: Callable that runs custom activation logic.
    :param script_path: Absolute path of the script to be run by the shell plugin.
    :param pathsep_join: String used to join paths in the shell.
    :param sep: String used to separate paths in the shell.
    :param path_conversion: Callable that converts a path to a shell-appropriate path.
    :param script_extension: Extension of the script to be run by the shell plugin.
    :param command_join: String used to join commands in the shell.
    :param run_script_tmpl: Template for running scripts in the shell.
    :param unset_var_tmpl: Template for unsetting a variable.
    :param export_var_tmpl: Template for exporting a variable.
    :param set_var_tmpl: Template for setting a variable.
    :param tempfile_extension: Extension of the temporary file created by the shell plugin.
    :param define_update_prompt: Callable that updates the shell prompt.
    """

    name: str
    summary: str
    osexec: bool
    custom: Callable[[PluginActivator, dict], SystemExit] | None
    script_path: str | None
    pathsep_join: str
    sep: str
    path_conversion: Callable[
        [str | Iterable[str] | None], str | tuple[str, ...] | None
    ]
    script_extension: str
    command_join: str
    run_script_tmpl: str
    unset_var_tmpl: str | None
    export_var_tmpl: str | None
    set_var_tmpl: str | None
    tempfile_extension: str | None
    define_update_prompt: Callable[[map, dict, str], None] | None
