#!/bin/sh
set -e

mkdir -p /var/log/nginx/

echo "Running service..."

PYTHONPATH=. socketshark -c local &

echo "Running health check"
uwsgi health.ini &

echo "Running nginx"
nginx -c /projects/service-exo-broker/nginx.conf  -g 'pid /tmp/nginx.pid;'

# Avoid exiting this script (PID 1)
tail -f /dev/null
