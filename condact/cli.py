# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import argparse
import sys

from conda.exceptions import conda_exception_handler
from conda.plugins import CondaSubcommand, hookimpl

from .shell_manager import update_plugin_manager, get_shell_syntax
from .logic import PluginActivator, _ActivatorChild
from .plugins import posix_cl, posix_ose

PLUGINS = [posix_cl, posix_ose]


def get_parsed_args(argv: list[str]) -> argparse.Namespace:
    """
    Parse CLI arguments to determine desired command.
    Create namespace with 'command' key, optional 'dev' key and, for activate only,
    optional 'env' and 'stack' keys.
    """
    parser = argparse.ArgumentParser(
        "conda shell",
        description="Process conda activate, deactivate, and reactivate",
    )
    # parser.add_argument(
    #     "-n",
    #     action="store",
    #     # metavar = "plugin_name",
    #     type=str,
    #     nargs="2",
    #     # required=True,
    #     dest="pn",
    #     help="The name of the conda shell plugin to use",
    # )
    parser.add_argument(
        '-p',
        '--plugin',
        action='store',
        help='The name of the conda shell plugin to use'
    )
    commands = parser.add_subparsers(
        required=True,
        dest="command",
    )

    activate = commands.add_parser(
        "activate",
        help="Activate a conda environment",
    )
    activate.add_argument(
        "env",
        metavar="env_name_or_prefix",
        default=None,
        type=str,
        nargs="?",
        help="""
            The environment name or prefix to activate. If the prefix is a relative path,
            it must start with './' (or '.\' on Windows). If no environment is specified,
            the base environment will be activated.
            """,
    )
    stack = activate.add_mutually_exclusive_group()
    stack.add_argument(
        "--stack",
        action="store_true",
        default=None,
        help="""
        Stack the environment being activated on top of the
        previous active environment, rather replacing the
        current active environment with a new one. Currently,
        only the PATH environment variable is stacked. This
        may be enabled implicitly by the 'auto_stack'
        configuration variable.
        """,
    )
    stack.add_argument(
        "--no-stack",
        dest="stack",
        action="store_false",
        default=None,
        help="Do not stack the environment. Overrides 'auto_stack' setting.",
    )
    activate.add_argument(
        "--dev", action="store_true", default=False, help=argparse.SUPPRESS
    )

    deactivate = commands.add_parser(
        "deactivate", help="Deactivate the current active conda environment"
    )
    deactivate.add_argument(
        "--dev", action="store_true", default=False, help=argparse.SUPPRESS
    )

    reactivate = commands.add_parser(
        "reactivate",
        help="Reactivate the current conda environment, updating environment variables",
    )
    reactivate.add_argument(
        "--dev", action="store_true", default=False, help=argparse.SUPPRESS
    )
    
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        # SystemExit: help blurb was printed, intercepting SystemExit(0) to avoid
        # plugins using classic activation logic causing the evaluation of help strings
        # by the shell interface
        raise SystemExit(1)

    return args


def add_subparsers(parser: argparse.ArgumentParser) -> None:
    """
    Add activate, deactivate and reactivate commands, along with associated sub-commands, to parser
    """
    pass


def print_activation_commands(activator: _ActivatorChild) -> int:
    """
    Print activation commands to stdout. Return 0 if successful, 1 if not.
    """
    print(activator.execute(), end="")
    return 0


def execute(argv: list[str]) -> SystemExit:
    """
    Get shell hook from named plugin. Raise error if no shell hooks are found.
    Run process associated with parsed CLI command (activate, deactivate, reactivate).
    """
    args = get_parsed_args(argv)
    pm = update_plugin_manager(PLUGINS)

    syntax = get_shell_syntax(pm, args.plugin)

    if syntax.osexec:
        activator = PluginActivator(syntax)
        cmds_dict = activator.parse_and_build(args)
        return activator.activate(cmds_dict)
    else:
        activator = _ActivatorChild(syntax, args)
        return sys.exit(conda_exception_handler(print_activation_commands, activator))


@hookimpl
def conda_subcommands():
    yield CondaSubcommand(
        name="shell",
        summary="Run plugins used for activate, deactivate, and reactivate",
        action=execute,
    )
