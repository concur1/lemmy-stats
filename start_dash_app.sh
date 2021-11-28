#!/bin/bash
source venv/bin/activate
gunicorn -w 3 app:server
