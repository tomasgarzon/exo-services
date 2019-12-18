#!/bin/bash
#
# 2019 OpenExO
#
# Database anonymize script, the anonymized dump with avatars will be placed in s3
#
set -e

# Get the TAG from .env file in home (production)
CURRENT_TAG=$(grep -E "TAG=(.*)" /home/ubuntu/.env | cut -c 5-)

# If no parameter is passed asks the user for tag
if [ -z "$1" ]; then
	read -e -p "Please, enter TAG to use for anonymizer [$CURRENT_TAG]: " TAG
fi

export TAG="${TAG:-${CURRENT_TAG}}"

# set dates for backup rotation
NOWDATE=`date +%Y-%m-%d`

# set backup directory variables
export SRCDIR=/tmp/anonymize/$NOWDATE
OUTDIR=/tmp/anonymize/$NOWDATE/out
BUCKET=exoleverbackup
HASH=$(date +%s | md5sum | cut -d' ' -f1)
DESTDIR=backup/exolever_anonymized/$NOWDATE-$HASH
DESTDIR_LATEST=backup/exolever_anonymized/latest

# database access details
HOST='platform-openexo.c8tf9qym4u1n.us-east-1.rds.amazonaws.com'
PORT='5432'
USER='exolever'
export PGPASSWORD='exolever'

export DB_DUMP_URL=http://nginx

SCRIPT_PATH=/home/ubuntu/deploy/developers/docker-compose.yml
SCRIPT_PATH_NGINX=/home/ubuntu/deploy/production/scripts/docker-compose-nginx.yml

#### END CONFIGURATION ####



function clean_deploy {

    docker-compose --file $SCRIPT_PATH --project-name anonymize down -v --remove-orphans
    rm -rf $SRCDIR/*
}

clean_deploy

# make the temp directory if it doesn't exist
mkdir -p $OUTDIR

# get list of databases
DBLIST=`psql -l -h$HOST -p$PORT -U$USER \
| awk '{print $1}' | grep -v "+" | grep -v "Name" | \
grep -v "List" | grep -v "(" | grep -v "template" | \
grep -v "postgres" | grep -v "root" | grep -v "rdsadmin" | grep -v "|" | grep -v "|"`

# Remove unused databases
DBLIST=${DBLIST//openexo/}
DBLIST=${DBLIST//exolever/}
DBLIST=${DBLIST//service_exo_mail/}

# dump each database to its own sql file
for DB_NAME in ${DBLIST}
do
	echo "Downloading $DB_NAME database dump..."
	pg_dump --host=$HOST --port=$PORT --username=$USER --dbname=$DB_NAME --no-owner --format=custom --create --quote-all-identifiers | gzip > $SRCDIR/$DB_NAME.dump.gz
done

# TODO: Disabled because avatars in prod are too big (more than 20Gb)
# echo "Copying production /media files (avatars)..."
# docker cp ubuntu_service-exo-core_1:/projects/service-exo-core/media/ $SRCDIR
# tar -zcf $SRCDIR/media.tar.gz -C $SRCDIR media


sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize pull

# Commented code for debug individual services
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --file docker-compose-nginx.yml --project-name anonymize up -d postgres redis nginx
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --file docker-compose-nginx.yml --project-name anonymize run service-exo-exq tail -f /dev/null
# End of Commented code for debug individual services

# Starting services (we must start before nginx to be firstly available)
sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --file $SCRIPT_PATH_NGINX --project-name anonymize up -d --remove-orphans nginx
sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --file $SCRIPT_PATH_NGINX --project-name anonymize up -d --remove-orphans

sleep 10s
until $(curl --output /dev/null --silent --head --fail http://localhost:6666/healthcheck/); do
    echo 'Waiting to service-exo-core to be ready...'
    sleep 5s
done

# TODO: Use a foreach approach when all services have the same anonymizer library
# # Replace _ per - (databases have underscores and services dash)
# SERVICELIST=${DBLIST/_/-}

# TODO: Disabled because avatars in prod are too big (more than 20Gb)
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-core tar --create --to-stdout media | gzip >  $OUTDIR/media.tar.gz

# Fix while we are not restoring avatars
sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-core mkdir -p media/avatars

sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-core python3 manage.py anonymize_users

for DB_NAME in $DBLIST; do
  echo "Anonymizing data..."
  SERVICE_NAME=${DB_NAME//_/-}
  sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T $SERVICE_NAME python3 manage.py anonymize_db --soft_mode
done


# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-auth python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-conversations python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-companies python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-events python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-exq python3 manage.py anonymize_db --soft_mode
# # sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-mail python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-medialibrary python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-opportunities python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-payments python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-projects python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-website python3 manage.py anonymize_db --soft_mode
# sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T service-exo-core python3 manage.py anonymize_db --soft_mode



for DB_NAME in $DBLIST; do
	echo "Dumping $DB_NAME anonymized database..."
    sed -e s/8000:80/6666:80/ -e /tty:\ true/d -e /stdin_open:\ false/d $SCRIPT_PATH | docker-compose --file /dev/stdin --project-name anonymize exec -T postgres pg_dump --username=exolever --dbname=$DB_NAME --no-owner --format=custom --create --quote-all-identifiers | gzip > $OUTDIR/$DB_NAME.dump.gz
done


echo "Upload anonymized backup to s3..."
s3cmd --acl-public put $OUTDIR/*.gz s3://$BUCKET/$DESTDIR/
s3cmd put $OUTDIR/*.gz s3://$BUCKET/$DESTDIR_LATEST/

curl -X POST \
  "https://ldjsgfq0u7.execute-api.us-east-1.amazonaws.com/prod/message?key=RwwrNbZM7A8dn2TB" \
  -d "room=devops&message=New anonymized database generated: https://${BUCKET}.s3.amazonaws.com/${DESTDIR}"

trap clean_deploy EXIT
