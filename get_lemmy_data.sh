#!/bin/bash
cd lemmy-stats
source venv/bin/activate
mkdir -p logs
python fetch_and_save.py
python insert_into_historical.py
deactivate


