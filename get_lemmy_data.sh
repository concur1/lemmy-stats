#!/bin/bash
source lemmy-stats/venv/bin/activate
cd lemmy-stats
mkdir -p logs
python fetch_and_save.py
python insert_into_historical.py
deactivate


