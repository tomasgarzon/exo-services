#!/bin/sh

# set backup directory variables
TMPDIR=$(mktemp --directory)
DESTDIR='backup/exolever_prod/media'
BUCKET='exoleverbackup'

echo "Sync media to s3..."
docker cp ubuntu_service-exo-core_1:/projects/service-exo-core/media/ $TMPDIR
s3cmd sync --recursive --skip-existing $TMPDIR s3://$BUCKET/$DESTDIR/
rm -rf $TMPDIR