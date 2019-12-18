#!/bin/bash

#### BEGIN CONFIGURATION ####

# set dates for backup rotation
NOWDATE=`date +%Y-%m-%d`
LASTDATE=$(date +%Y-%m-%d --date='1 month ago')

# set backup directory variables
SRCDIR='/tmp/s3backups'
DESTDIR='backup/exolever_prod'
BUCKET='exoleverbackup'

# database access details
HOST='platform-openexo.c8tf9qym4u1n.us-east-1.rds.amazonaws.com'
PORT='5432'
USER='exolever'
export PGPASSWORD='exolever'
#### END CONFIGURATION ####

# make the temp directory if it doesn't exist
mkdir -p $SRCDIR/$NOWDATE

# get list of databases
DBLIST=`psql -l -h$HOST -p$PORT -U$USER \
| awk '{print $1}' | grep -v "+" | grep -v "Name" | \
grep -v "List" | grep -v "(" | grep -v "template" | \
grep -v "postgres" | grep -v "root" | grep -v "rdsadmin" | grep -v "|" | grep -v "|"`

# Remove unused databases
DBLIST=${DBLIST//openexo/}
DBLIST=${DBLIST//exolever/}

# If no parameter is passed omit the service_exo_mail database
if [ -z "$1" ]; then
	DBLIST=${DBLIST//service_exo_mail/}
	echo "Bypass the service_exo_mail database dump. Pass a parameter to dump it"
fi

# dump each database to its own sql file
for DB_NAME in ${DBLIST}
do
	echo "Downloading $DB_NAME database dump..."
	# pg_dump -h -p$PORT -U$USER $DB_NAME -Fc -Z 9 -f $SRCDIR/$DB_NAME.sql
	pg_dump --host=$HOST --port=$PORT --username=$USER --dbname=$DB_NAME --no-owner --format=custom --create --quote-all-identifiers | gzip > $SRCDIR/$NOWDATE/$DB_NAME.dump.gz
done

echo "Upload backup to s3..."
s3cmd put $SRCDIR/$NOWDATE/*.dump.gz s3://$BUCKET/$DESTDIR/$NOWDATE/

echo "Delete old backups from s3"
s3cmd del --recursive s3://$BUCKET/$DESTDIR/$LASTDATE/*.dump.gz

# remove all files in our source directory
cd
rm -rf $SRCDIR/$LASTDATE

