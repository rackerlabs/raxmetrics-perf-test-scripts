#!/bin/bash

topsrc="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # this gives you the directory where this script is located
source $topsrc/set-env.bash
java net.grinder.Console
