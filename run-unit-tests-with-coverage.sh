#!/bin/bash

topsrc=`dirname $0`  # this gives you the directory where this script is located
cd $topsrc
coverage run --source=abstract_thread,annotationsingest,authenticating_request,config,connector,exception_handling_request,get_user,grinder,grinder_connector,http_failure_exception,ingest,ingestenum,nvpair,py_java,query,requests_connector,response_checking_request,thread_manager,throttling_group,throttling_request,user scripts/tests.py
coverage html

