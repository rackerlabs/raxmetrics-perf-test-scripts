#!/bin/bash

topsrc=`dirname $0`  # this gives you the directory where this script is located
cd $topsrc
. $topsrc/set-env.sh
java -cp  dependencies/grinder-3.11/lib/grinder.jar:dependencies/jyson-1.0.2/lib/jyson-1.0.2.jar net.grinder.Grinder properties/grinder-unittests.properties
