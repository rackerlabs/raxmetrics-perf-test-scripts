#!/bin/bash

mkdir -p dependencies
cd dependencies

wget -O grinder-3.11-binary.zip 'http://downloads.sourceforge.net/project/grinder/The%20Grinder%203/3.11/grinder-3.11-binary.zip'
unzip grinder-3.11-binary.zip
chmod 755 grinder-3.11

wget -O jyson-1.0.2.zip http://opensource.xhaus.com/attachments/download/3/jyson-1.0.2.zip
unzip jyson-1.0.2.zip