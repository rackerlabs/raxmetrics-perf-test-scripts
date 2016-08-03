#!/bin/bash

coverage run --source=abstract_thread,annotationsingest,ingest,ingestenum,query,thread_manager scripts/tests.py
coverage html

