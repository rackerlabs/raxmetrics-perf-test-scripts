#!/bin/bash

coverage run --source=abstract_thread,annotationsingest,ingest,ingestenum,query,thread_manager,config,throttling_group scripts/tests.py
coverage html

