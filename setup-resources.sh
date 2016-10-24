#!/bin/bash

topsrc=`dirname $0`  # this gives you the directory where this script is located

mkdir -p $topsrc/dependencies
cd $topsrc/dependencies

wget -O grinder-3.11-binary.zip 'http://downloads.sourceforge.net/project/grinder/The%20Grinder%203/3.11/grinder-3.11-binary.zip'
unzip grinder-3.11-binary.zip
chmod 755 grinder-3.11

wget -O jyson-1.0.2.zip http://opensource.xhaus.com/attachments/download/3/jyson-1.0.2.zip
unzip jyson-1.0.2.zip

wget -O jasypt-1.9.2-dist.zip http://downloads.sourceforge.net/project/jasypt/jasypt/jasypt%201.9.2/jasypt-1.9.2-dist.zip
unzip jasypt-1.9.2-dist.zip
find jasypt-1.9.2 -type d -exec chmod 755 {} +
