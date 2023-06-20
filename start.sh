#!/bin/bash
python -m webbrowser "http://127.0.0.1:5000"
gunicorn -w 1 --threads 100 -b 127.0.0.1:5000 server:app

