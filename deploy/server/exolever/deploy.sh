#!/bin/bash
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
if [[ $# -ne 1 && $# -ne 2 && $# -ne 3 ]] ; then
    echo_blue "Please provide branch name and an optional subdomain"
    echo_yellow "Usage: $0 EXO-1273-MVF [exo1273] [anonimized_database_url]"
    exit 1
fi

TAG=$1
SUBDOMAIN=$2
DB_DUMP_URL=$3
DOMAIN=$(hostname)

# if you don't pass the second argument, it generates automatically
if [ -z $2 ]; then
    SUBDOMAIN=exo$(echo "${TAG}" | sed "s/[^0-9]*//g")
fi


# chequed that the directory exists, and if it already exists let you know
if [ -d "$SUBDOMAIN" ]; then
    echo_blue "Warning, the $SUBDOMAIN directory already exists"
    if [ ! -t 0 ]; then # Non-Interactive tty
        echo "Deploy aborted on non-tty"
        exit 0
    fi
    read -p "Do you want to continue? [yN] " -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo_yellow "Deploy aborted!"
        exit 1
    fi

fi

mkdir -p $SUBDOMAIN

# when the name contains '/' changes to '_'
TAG=$(echo "${TAG//[\/]/_}")

sed -e "s/\${TAG}/$TAG/" -e "s/\${SUBDOMAIN}/$SUBDOMAIN/" -e "s/\${DOMAIN}/$DOMAIN/" docker-compose-template.yml > $SUBDOMAIN/docker-compose.yml
cp .env $SUBDOMAIN/.env

if [ ! -z $DB_DUMP_URL ]; then
    # Get the latest anonymized database url via s3cmd command
    if [ "$DB_DUMP_URL" = "latest" ]; then
        DB_DUMP_URL=$(s3cmd ls s3://exoleverbackup/backup/exolever_anonymized/ | tail -3 | head -1 | tr -s " " |  awk '{ print $2 }' | sed s/s3/http/ | sed s/exoleverbackup/exoleverbackup.s3.amazonaws.com/ | sed s/.$//)
    fi

    sed -i -e "s|# DB_DUMP_URL.*|DB_DUMP_URL:\ $DB_DUMP_URL|g" $SUBDOMAIN/docker-compose.yml
fi

docker-compose -p $SUBDOMAIN -f $SUBDOMAIN/docker-compose.yml down -v --remove-orphans
docker-compose -p $SUBDOMAIN -f $SUBDOMAIN/docker-compose.yml pull
docker-compose -p $SUBDOMAIN -f $SUBDOMAIN/docker-compose.yml up -d --remove-orphans

echo ""
echo_yellow "Deployment created sucesfully! ($(pwd)/$SUBDOMAIN)"
echo_green  "Open https://$SUBDOMAIN.$DOMAIN in your browser"
