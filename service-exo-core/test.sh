#!/bin/sh

export DEBUG='True'
export FORCE_SCRIPT_NAME=''
export DB_HOST=localhost
export DB_USER=postgres
export POPULATOR_MODE='True'
export REDIS_HOST=localhost
export MASTER_PASSWORD='.eeepdQA'

apk add --no-cache \
    python3-dev \
    build-base \
    postgresql  \
    postgresql-contrib \
    openrc \
    git \
    redis \
    graphviz-dev

# Install devel requirements
pipenv install --system --dev --skip-lock

# Running linter and basich django check
flake8 --config ./scripts/flake8.cfg .
pycodestyle --config ./scripts/pep8.cfg .


mkdir -p /projects/service-exo-core/exo-backoffice/templates/exo-backoffice
touch /projects/service-exo-core/exo-backoffice/__init__.py
touch /projects/service-exo-core/exo-backoffice/templates/exo-backoffice/base.html

# Running postgresql inside alpine (TODO, find a better way to do this without openrc)
mkdir -p /run/openrc/ /run/postgresql
touch /run/openrc/softlevel
chmod 777 /run/postgresql

/etc/init.d/postgresql setup 2> /dev/null
su - postgres -c 'pg_ctl -D /var/lib/postgresql/11/data/ start' \
    && redis-server --daemonize yes \
    && echo "\033[0m" \
    && if [ "$FORCE_TESTS" == "1" ] || [ "$SOURCE_NAME" == "devel" ] || [ "$(printf "%s\n" "$SOURCE_NAME" | awk '/^release-/')" ] ; then \
        python3 manage.py test --noinput --parallel=8; \
    fi \
    && psql -U postgres -c "CREATE DATABASE ${DB_NAME};" \
    && time python3 manage.py migrate \
    && time python3 manage.py populate \
    && pg_dump --username=postgres --dbname=$DB_NAME --no-owner --format=custom --create --compress=9 --quote-all-identifiers | gzip > $DB_NAME.dump.gz \
    && tar -zcf media.tar.gz media \
    && python3 manage.py anonymize
