#!/bin/bash
set -e

# Console colors
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;36m"
RED="\033[1;31m"
RESET="\033[0m"

echo_green() {
    echo -e "$GREEN$1$RESET"
}
echo_yellow() {
    echo -e  "$YELLOW$1$RESET"
}
echo_blue() {
    echo -e  "$BLUE$1$RESET"
}
echo_red() {
    echo -e  "$RED$1$RESET"
}

read -p "Do you want to update OpenExO Platform? [yN] " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    CURRENT_TAG=$(grep -E "TAG=(.*)" .env | cut -c 5-)
    read -e -p "Please, enter TAG to deploy [$CURRENT_TAG]: " NEW_TAG
    NEW_TAG="${NEW_TAG:-${CURRENT_TAG}}"
    if [ $CURRENT_TAG != $NEW_TAG ]
    then
        sed -i "s/TAG=.*/TAG=$NEW_TAG/" .env
    fi
    export TAG=$NEW_TAG

    echo ""
    read -p "Do you want to backup your current data? [yN] " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo ""
        echo_yellow "Making postgres backup..."
        source ~/scripts/s3-postgresql-backup.sh

    fi

    if ! curl -o /dev/null --silent --fail https://cdn.openexo.com/bundles/exo-frontend/$TAG/index.html; then
        echo "Error: exo-frontend:${TAG} doesn't exist on s3!"
        exit 2
    fi

    echo_yellow "Updating deploy files..."
    git archive --format=tar --remote=git\@bitbucket.org:exolever/exo-services.git --prefix=deploy/ master:deploy/ | tar xf -

    echo ""
    echo_yellow "Updating Docker microservices (exo-services)..."
    docker-compose pull
    docker-compose up -d --remove-orphans

    echo_yellow "Send e-mail notification to admins..."
    docker-compose exec service-exo-core python3 manage.py sendtestemail --admins

    echo_yellow "Cleaning unused Docker images!"
    docker system prune --all --force

    curl -X POST \
      "https://ldjsgfq0u7.execute-api.us-east-1.amazonaws.com/prod/message?key=RwwrNbZM7A8dn2TB" \
      -d "room=%5BREAD-ONLY%5D%20release_delivery&message=${NEW_TAG}%20deployed!"


    echo_yellow "Checking status"
    curl --silent https://platform.openexo.com/healthcheck/ | jq -s '.[]' | sed -e 's/^[ \t]*//' -e 's/[ \t]*$//'  | grep status

    echo ""
    echo_yellow "Deploy finished!"
else
    echo ""
    echo_red "Update aborted!!"
fi

echo ""
