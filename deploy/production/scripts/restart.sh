#!/bin/bash
#
# 2019 OpenExO
#
# Script to restart services
#
set -e

# Console colors
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;36m"
RESET="\033[0m"

echo_green() {
    echo -e "$GEEN$1$RESET"
}
echo_yellow() {
    echo -e  "$YELLOW$1$RESET"
}

echo_blue() {
    echo -e  "$BLUE$1$RESET"
}


# You must provide almost the branch name
if [[ $# -ne 2 ]] ; then
    echo "Please provide service name and program optional subdomain"
    echo "Usage: $0 <service-name> <program>"
    echo_yellow "Example: $0 service-exo-auth gunicorn"
    exit 1
fi

SERVICE=$1
PROGRAM=$2

case "$PROGRAM" in
	"gunicorn")

		if [ "$SERVICE" == "service-exo-medialibrary" ]; then
			echo_yellow "ERROR: $PROGRAM is not supported in service-exo-medialibrary"
			exit 1
		fi

		docker-compose exec $SERVICE pkill gunicorn
		docker-compose exec --detach $SERVICE gunicorn service.wsgi:application --name $SERVICE --workers 2 --timeout 30 --log-level=INFO --log-file=- --bind=0.0.0.0:8000
    ;;
	"daphne")
		
		if [ "$SERVICE" != "service-exo-medialibrary" ]; then
			echo_yellow "ERROR: $PROGRAM is only supported in service-exo-medialibrary"
			exit 1
		fi

		docker-compose exec --detach $SERVICE pkill daphne
		docker-compose exec --detach $SERVICE daphne service.asgi:application -v 2 --ws-protocol "graphql-ws" --proxy-headers --access-log=- -b 0.0.0.0 -p 8000
	;;
	"celery")
		docker-compose exec --detach $SERVICE pkill -f "celery worker --app service --loglevel=INFO";
		docker-compose exec --detach $SERVICE celery worker --app service --loglevel=INFO
	;;
	"celerybeat")

		if [ "$SERVICE" != "service-exo-core" ]; then
			echo_yellow "ERROR: $PROGRAM is only supported in service-exo-core"
			exit 1
		fi

		docker-compose exec --detach $SERVICE celery multi stop workername --pidfile=celerybeat.pid
		docker-compose exec --detach $SERVICE celery -A service beat --loglevel=INFO
	;;
	"nginx")

		if [ "$SERVICE" != "service-exo-broker" ]; then
			echo_yellow "ERROR: $PROGRAM is only supported in service-exo-broker"
			exit 1
		fi

		docker-compose exec --detach $SERVICE pkill nginx
		docker-compose exec --detach nginx -c /projects/service-exo-broker/nginx.conf  -g 'pid /tmp/nginx.pid;'
    ;;
*)
    echo_yellow "Program $PROGRAM not supported"
    ;;
esac

