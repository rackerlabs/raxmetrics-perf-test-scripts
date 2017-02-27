#!/bin/sh

topsrc="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # this gives you the directory where this script is located

mkdir -p $topsrc/dependencies

unzip $topsrc/dependencies/grinder-3.11-binary.zip -d $topsrc/dependencies/
chmod 755 $topsrc/dependencies/grinder-3.11

unzip $topsrc/dependencies/jyson-1.0.2.zip -d $topsrc/dependencies/

unzip $topsrc/dependencies/jasypt-1.9.2-dist.zip -d $topsrc/dependencies/
find $topsrc/dependencies/jasypt-1.9.2 -type d -exec chmod 755 {} +
