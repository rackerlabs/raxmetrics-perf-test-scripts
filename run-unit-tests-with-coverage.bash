#!/bin/bash

topsrc="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # this gives you the directory where this script is located
coverage run --source=abstract_thread,annotationsingest,authenticating_request,config,connector,exception_handling_request,get_user,grinder,grinder_connector,http_failure_exception,ingest,nvpair,py_java,query,requests_connector,response_checking_request,thread_manager,throttling_group,throttling_request,user $topsrc/scripts/tests.py
coverage html --directory=$topsrc/htmlcov

