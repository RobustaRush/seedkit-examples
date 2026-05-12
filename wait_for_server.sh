#!/bin/bash
MAX_ATTEMPTS=15
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://127.0.0.1:8000/admin/login/ > /dev/null; then
        echo "Server is up!"
        exit 0
    fi
    echo "Waiting for server to be up... (Attempt $((ATTEMPT+1))/$MAX_ATTEMPTS)"
    sleep 2
    ATTEMPT=$((ATTEMPT+1))
done
echo "Server did not come up within the expected time."
exit 1