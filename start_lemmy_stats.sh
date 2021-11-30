#!/bin/bash

pkill gunicorn
source venv/bin/activate
gunicorn -w 3 index:server &
watch -n 1200 get_lemmy_data.sh