#!/bin/bash

topsrc=`dirname $0`  # this gives you the directory where this script is located
cd $topsrc
coverage run --source=abstract_thread,annotationsingest,ingest,ingestenum,query,thread_manager,config,throttling_group scripts/tests.py
coverage html

