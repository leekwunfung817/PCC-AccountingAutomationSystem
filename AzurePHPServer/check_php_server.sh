#!/bin/bash

# Config
PORT=8080
RESTART_SCRIPT="/home/site/wwwroot/php_server.sh"

# Check if PHP server is running on the given port
if ! lsof -i :$PORT | grep -q "php"; then
    echo "$(date): PHP server not running, restarting..."
    nohup $RESTART_SCRIPT >/dev/null 2>&1 &
else
    echo "$(date): PHP server is healthy."
fi

