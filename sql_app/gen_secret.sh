#!/bin/env bash

# TODO: set a user only umask for proper premissions
# Mar 23, 2022 - H.B.


if [ -z $(command -v openssl) ]
then
    echo "openssl not installed"
    exit 1
fi

openssl rand -hex 32
