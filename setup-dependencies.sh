#!/bin/bash

topsrc=`dirname $0`  # this gives you the directory where this script is located

mkdir -p $topsrc/dependencies
cd $topsrc/dependencies

unzip grinder-3.11-binary.zip
chmod 755 grinder-3.11

unzip jyson-1.0.2.zip

unzip jasypt-1.9.2-dist.zip
find jasypt-1.9.2 -type d -exec chmod 755 {} +
