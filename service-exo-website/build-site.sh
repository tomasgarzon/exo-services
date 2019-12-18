#!/bin/sh

set -e

# Json file with sections
JSON_FILE=$1

# Extract json fields
PK=$(cat $JSON_FILE | jq --raw-output .pk)
UUID=$(cat $JSON_FILE | jq --raw-output .uuid)
SLUG=$(cat $JSON_FILE | jq --raw-output .slug)
THEME=$(cat $JSON_FILE | jq --raw-output .theme)
DOMAIN=$(cat $JSON_FILE | jq --raw-output .domain)
STATUS=$(cat $JSON_FILE | jq --raw-output .status)

# generate image
cd banner
python3 banner.py -f $JSON_FILE
cd ..

# Copying json
cp $JSON_FILE ./hugo_site/data/sections.json

# Build the site (in $SLUG dir)
hugo --source hugo_site --theme $THEME --destination /var/www/$SLUG --verbose --debug

# Tags should go to "production folder"
if [ ! -z $SOURCE_TAG ]; then
    export SOURCE_NAME=production
fi

# Upload to S3 and delete local generated site to save space (in background)
if [ ! -z $AWS_KEY ]; then

	(s3cmd \
	    --access_key=$AWS_KEY \
	    --secret_key=$AWS_SECRET \
	    --force \
	    --delete-removed \
	    --human-readable-sizes \
	    --stop-on-error \
	    --acl-public \
	    --guess-mime-type \
	    --no-mime-magic \
	    --recursive \
	    sync /var/www/$SLUG/* \
	    s3://$AWS_BUCKET/bundles/$SERVICE_NAME/$SOURCE_NAME/$SLUG/;
	rm -rf /var/www/$SLUG/) &

	# In preview we should wait instead of sending in background
	[  "$STATUS" == 'preview' ] && { echo "Waiting for pushing preview"; wait; }

fi

# Delete sections json file
rm ./hugo_site/data/sections.json

