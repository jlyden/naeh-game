#!/bin/bash

# https://localtunnel.github.io/www/
# https://github.com/localtunnel/localtunnel/issues/81

function localtunnel {
lt -s naehgamedemo --port 5000
}

until localtunnel; do
echo "localtunnel server crashed"
sleep 2
done
