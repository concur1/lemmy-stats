#!/bin/bash
cd /home/project/lemmy-crawler-python/
source venv/bin/activate
gunicorn -w 3 app:server
