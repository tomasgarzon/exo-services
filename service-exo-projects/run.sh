#!/bin/sh
set -e

if [ "$DEBUG" == "True" ] ; then
    echo "Installing development requirements..."
    pip3 install django-debug-toolbar
fi


# Wait to PosgreSQL server to be available
until PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -c '\q' 2> /dev/null; do
  >&2 echo "Postgres is unavailable - sleeping..."
  sleep 1
done

# Checking if database has data
if ! PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1; then

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
fi

echo "Running migrations..."
python3 manage.py migrate

echo "Apply changelogs ..."
python3 manage.py applychange

# Wait to Redis server to be available
until ((printf "PING\r\n";) | nc $REDIS_HOST 6379 | grep -q +PONG) ; do
>&2 echo "Redis is unavailable - sleeping..."
  sleep 1
done

echo "Collecting static..."
python3 manage.py collectstatic --noinput

echo "Runing worker..."
# Run worker
celery worker --app service --loglevel INFO &

echo "Starting autobackup..."
# Start the autobackup
python3 schedule_task.py &

# Runing gunicorn
gunicorn service.wsgi:application --name $SERVICE_NAME --workers 2 --timeout 30 --log-level=INFO --log-file=- --bind=0.0.0.0:8000 &

# Avoid exiting this script (PID 1)
tail -f /dev/null
