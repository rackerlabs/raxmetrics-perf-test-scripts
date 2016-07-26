#!/bin/bash

. ./set-env.sh
java -cp  dependencies/grinder-3.11/lib/grinder.jar:dependencies/jyson-1.0.2/lib/jyson-1.0.2.jar net.grinder.Grinder properties/grinder.properties
