#!/bin/bash
# python clearJobs.py
until python worker.py; do
    echo "'worker.py' crashed with exit code $?. Restarting..." >&2
    sleep 1
done
