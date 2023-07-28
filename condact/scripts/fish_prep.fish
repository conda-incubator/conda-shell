# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
# update conda function to evaluate shell arguments

function conda --inherit-variable CONDA_EXE
    if [ (count $argv) -lt 1 ]
        $CONDA_EXE
    else
        set -l cmd $argv[1]
        set -e argv[1]
        switch $cmd
            case activate deactivate
                eval ($CONDA_EXE shell.fish $cmd $argv)
            case shell
                eval ($CONDA_EXE $cmd $argv)
            case install update upgrade remove uninstall
                $CONDA_EXE $cmd $argv
                and eval ($CONDA_EXE shell.fish reactivate)
            case '*'
                $CONDA_EXE $cmd $argv
        end
    end
end
