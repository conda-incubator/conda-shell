#!/bin/sh

if [ "$1 $2 $3 $4" = "conda shell -n posix_cl" ]; then
    # Evaluate the return statement (all arguments except the first four)
    eval "$@"
else
    # If the condition is not met, simply execute the command as is
    "$@"
fi