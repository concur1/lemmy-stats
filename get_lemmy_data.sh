#!/bin/bash
source /home/project/lemmy-crawler-python/venv/bin/activate
cd /home/project/lemmy-crawler-python/
mkdir -p logs
python fetch_and_save.py
python convert_to_csv.py
deactivate


