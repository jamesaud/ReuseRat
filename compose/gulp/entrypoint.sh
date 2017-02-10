#!/bin/bash
set -e
cmd="$@"

echo 'Starting Gulp Service'

if [ -d /CREATE_ON_FIRST_RUN ]; then
    true  # Do nothing
else
    if [ -d node_modules ]; then 
        echo "Deleting node_modules folder to configure binary for this container"
        rm -r node_modules;
    fi
    echo "Installing node requirements"
    npm install
    mkdir /CREATE_ON_FIRST_RUN
fi

echo "Gulp is up and running..."

exec $cmd
