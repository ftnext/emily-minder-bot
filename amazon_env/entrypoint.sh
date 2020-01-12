#!/bin/bash
set -eu
BUNDLE_ZIP_FILE=/var/task/bundle.zip

python3 -m pip install -t . -r requirements.txt
zip -r9 $BUNDLE_ZIP_FILE *
zip -gr9 $BUNDLE_ZIP_FILE .[^.]*
