#!/bin/zsh

export FLASK_RUN_HOST="localhost"
export FLASK_RUN_PORT=5000
chmod +x run_worker.sh
./run_worker.sh &
flask run
