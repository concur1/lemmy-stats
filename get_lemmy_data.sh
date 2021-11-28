#!/bin/bash
source lemmy-stats/venv/bin/activate
mkdir -p logs
python lemmy-stats/fetch_and_save.py
python lemmy-stats/insert_into_historical.py
deactivate


