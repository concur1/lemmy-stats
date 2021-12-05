#!/bin/bash
pkill gunicorn
source venv/bin/activate
gunicorn -w 3 index:server &
mkdir -p logs
python get_lemmy_data.py 1200 >logs/get_lemmy_data.log 2>&1 < logs/get_lemmy_data.log &
