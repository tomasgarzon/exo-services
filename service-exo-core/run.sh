#!/bin/sh
#
#
# Docker deploy start script
#

# Console colors
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;36m"
RESET="\033[0m"

echo_red() {
    echo -e "$RED$1$RESET"
}

echo_green() {
    echo -e "$GREEN$1$RESET"
}
echo_yellow() {
    echo -e  "$YELLOW$1$RESET"
}

echo_blue() {
    echo -e  "$BLUE$1$RESET"
}


if [ "$DEBUG" = "True" ] ; then
    echo "Installing development requirements..."
    pip3 install django-debug-toolbar
fi

echo_blue "Creating /run/ and /var/log/ dirs"
mkdir -p /projects/service-exo-core/run
# mkdir -p /var/log/nginx/
mkdir -p /var/log/supervisor/
mkdir -p /projects/service-exo-core/media/avatars

echo_blue "Collecting statics..."
python3 manage.py collectstatic --no-input 2>&1 > /var/log/collectstatic.log &

# Wait to PosgreSQL server to be available
until PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -c '\q' 2> /dev/null; do
   >&2 echo "Postgres is unavailable - sleeping..."
   sleep 1
done


# Check if the deploy was previously populated (DB_NAME has tables, because the database is always created)
TABLES=$(PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -tc "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog');")
if [ "$TABLES" -gt "0" ] ; then

    echo_yellow "-------------------------------------------------"
    echo_yellow "Congratulations! I found previous database data, "
    echo_yellow "bypassing population! "
    echo_yellow "-------------------------------------------------"

else

    export URL_BUNDLES_POPULATOR=https://s3.amazonaws.com/openexo/bundles/populator/$SOURCE_NAME

    # Check if anonymized dump passed
    if [ -z "$DB_DUMP_URL" ]; then
        echo "No anonymized dump URL pased, using regular populator dump."
        export DB_DUMP_URL=$URL_BUNDLES_POPULATOR
    fi

    echo "Creating database..."
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

    # Restoring PostgreSQL database dump
    if [ "$(curl --silent --output /dev/null --head --write-out "%{http_code}" $DB_DUMP_URL/$DB_NAME.dump.gz)" == "200" ]; then
        echo "Downloading and restoring PostgreSQL database dump..."
        curl --silent --show-error $DB_DUMP_URL/$DB_NAME.dump.gz | zcat | PGPASSWORD=$DB_PASS pg_restore --username=$DB_USER --host=$DB_HOST --dbname=$DB_NAME --no-owner --role=exolever --no-privileges --single-transaction --verbose &> /var/log/pg_restore.log
        echo done
    elif [ "$(curl --silent --output /dev/null --head --write-out "%{http_code}" https://s3.amazonaws.com/openexo/bundles/populator/devel/$DB_NAME.dump.gz)" == "200" ]; then
        echo "Downloading and restoring PostgreSQL database dump..."
        curl --silent --show-error https://s3.amazonaws.com/openexo/bundles/populator/devel/$DB_NAME.dump.gz | zcat | PGPASSWORD=$DB_PASS pg_restore --username=$DB_USER --host=$DB_HOST --dbname=$DB_NAME --no-owner --role=exolever --no-privileges --single-transaction --verbose &> /var/log/pg_restore.log
        echo done
    else
        echo "ERROR: PostgreSQL database dump not found in $DB_DUMP_URL/$DB_NAME.dump.gz"
        exit 2
    fi

    # Restoring media files (avatars)
    if [ "$(curl --silent --output /dev/null --head --write-out "%{http_code}" $DB_DUMP_URL/media.tar.gz)" == "200" ]; then
        echo_blue "Restoring media files (avatars)..."
        curl --silent --show-error $DB_DUMP_URL/media.tar.gz | tar xzv &> /var/log/media_restore.log
    elif [ "$(curl --silent --output /dev/null --head --write-out "%{http_code}" https://s3.amazonaws.com/openexo/bundles/populator/devel/media.tar.gz)" == "200" ]; then
        echo_blue "Restoring media files (avatars)..."
        curl --silent --show-error https://s3.amazonaws.com/openexo/bundles/populator/devel/media.tar.gz | tar xzv &> /var/log/media_restore.log
    else
        echo_red "ERROR: media dump not found"
    fi

fi

echo "Running migrations..."
python3 manage.py migrate

echo_blue "Running changelog..."
python3 manage.py applychange

# Wait to Redis server to be available
until ((printf "PING\r\n";) | nc $REDIS_HOST 6379 | grep -q +PONG) ; do
>&2 echo "Redis is unavailable - sleeping..."
  sleep 1
done

echo "Runing celery worker..."
celery worker --app service --loglevel=INFO &

echo "Starting schedule task..."
python3 schedule_task.py &

echo "Running celerybeat..."
rm -f celerybeat.pid
celery beat --app service --loglevel=INFO &

echo "Running gunicorn..."
gunicorn service.wsgi:application --name $SERVICE_NAME --workers 2 --timeout 30 --log-level=INFO --log-file=- --bind=0.0.0.0:8000 &

# Avoid exiting this script (PID 1)
tail -f /dev/null
