#!/usr/bin/env bash
set -e

if [ -s /autograder/source/requirements.txt ]; then
    python3 -m pip install -r /autograder/source/requirements.txt
fi
