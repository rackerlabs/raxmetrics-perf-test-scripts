#!/bin/bash

topsrc="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # this gives you the directory where this script is located
. $topsrc/set-env.sh
java net.grinder.Grinder $topsrc/properties/grinder-unittests.properties
