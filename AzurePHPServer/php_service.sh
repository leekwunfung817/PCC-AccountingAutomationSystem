#!/bin/bash

# Folder to serve

DOCROOT="/home/site/wwwroot"

# Port to listen on
PORT=8080

# Command to run PHP server
CMD="php -S 0.0.0.0:$PORT -t $DOCROOT"

# Infinite loop to keep restarting if interrupted
while true; do
    echo "Starting PHP server on port $PORT serving $DOCROOT..."
    $CMD
    echo "PHP server stopped. Restarting in 5 seconds..."
    sleep 5
done


