#!/bin/sh

called=$_
topsrc="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # this gives you the directory where this script is located
export CLASSPATH=$topsrc/dependencies/grinder-3.11/lib/*:$topsrc/dependencies/jyson-1.0.2/lib/*:$topsrc/dependencies/jasypt-1.9.2/lib/*
