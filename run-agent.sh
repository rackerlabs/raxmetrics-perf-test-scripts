#!/bin/sh

PROPERTIES_FILE=$1
if [ -z "$PROPERTIES_FILE" ]; then
    echo Usage: $0 PROPERTIES_FILE
    exit 1
fi

topsrc="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # this gives you the directory where this script is located
source $topsrc/set-env.sh
java net.grinder.Grinder "$PROPERTIES_FILE"
