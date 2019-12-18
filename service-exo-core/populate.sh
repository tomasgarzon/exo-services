#!/bin/sh
#
#
# Backend populate script
#
set +e

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
    echo -e "$YELLOW$1$RESET"
}

echo_blue() {
    echo -e "$BLUE$1$RESET"
}


echo_yellow "WARNING! This script is temporary, until we have the exo-broker!!"


read -p "Do you want to delete your current databases? [yN] " -n 1 -r
# if [[ $REPLY =~ ^[Yy]$ ]]
if [ "$REPLY" != "${REPLY#[Yy]}" ]
then
    echo ""
    # Get current branch from git (without git command)
    CURRENT_SOURCE_NAME=$(cat ../.git/HEAD | cut -d '/' -f3) || echo "(unnamed branch)"

    # Set the tag
    CURRENT_SOURCE_NAME=${CURRENT_SOURCE_NAME:-$TAG}

    read -p "Please, enter from which branch are you geting populator data [$CURRENT_SOURCE_NAME]: " SOURCE_NAME
    SOURCE_NAME="${SOURCE_NAME:-${CURRENT_SOURCE_NAME}}"


    read -p "If you want, enter an anonimized database url [None]: " DB_DUMP_URL

    URL_BUNDLES_POPULATOR=https://s3.amazonaws.com/openexo/bundles/populator/$SOURCE_NAME

    DB_NAME=service_exo_core
    DB_USER=exolever
    DB_PASS=exolever
    DB_HOST=${DB_HOST:-localhost}

    echo_blue "Populating from $SOURCE_NAME branch..."

    # Wait to PosgreSQL server to be available
    until PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -c '\q' 2> /dev/null; do
      >&2 echo "Postgres is unavailable - sleeping..."
      sleep 1
    done

    # Ensure the old db is erased
    echo_blue "Deleting old database."
    TEMP_DB="temp_db"
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -c "CREATE DATABASE $TEMP_DB"
    echo_yellow "Temporary DB created"
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $TEMP_DB -c "DROP DATABASE $DB_NAME"
    echo_yellow "DB $DB_NAME deleted"
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $TEMP_DB -c "CREATE DATABASE $DB_NAME"
    echo_green "DB $DB_NAME freshly generated"
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -c "DROP DATABASE $TEMP_DB"
    echo_yellow "Temporary DB deleted"

    # Check if anonymized dump passed
    if [ -z "$DB_DUMP_URL" ]; then
        echo_yellow "No anonymized dump URL pased, using regular populator dump."
        DB_DUMP_URL=$URL_BUNDLES_POPULATOR
    fi

    # Restoring PostgreSQL database dump
    if [ "$(curl --silent --output /dev/null --head --write-out "%{http_code}" $DB_DUMP_URL/$DB_NAME.dump.gz)" == "200" ]; then
        echo_blue "Downloading and restoring PostgreSQL database dump..."
        curl --silent --show-error $DB_DUMP_URL/$DB_NAME.dump.gz | zcat | PGPASSWORD=$DB_PASS pg_restore -U $DB_USER -h $DB_HOST -d $DB_NAME --clean
        echo done
    else
        echo_red "ERROR: PostgreSQL database dump not found"
    fi

    # Restoring media files (avatars)
    if [ "$(curl --silent --output /dev/null --head --write-out "%{http_code}" $DB_DUMP_URL/media.tar.gz)" == "200" ]; then
        echo_blue "Restoring media files (avatars)..."
        curl --silent --show-error $DB_DUMP_URL/media.tar.gz | tar xz
    else
        echo_red "ERROR: media dump not found"
    fi

    echo_green "Population finished!"

fi
echo ""
