#!/bin/bash

# NOT USED, maybe we should remove this

SRCDIR='/home/ubuntu/projects/exolever/frontend/static/'

LISTDIR=(scripts/ maps/scripts maps/styles/ styles/)
S3NAME=exolever


remove_s3 () {
s3cmd ls s3://$1 | grep " DIR " -v | while read -r line;
  do
    createDate=`echo $line|awk {'print $1" "$2'}`
    createDate=`date -d"$createDate" +%s`
    olderThan=`date -d"-$2" +%s`
    if [[ $createDate -lt $olderThan ]]
      then
        fileName=`echo $line|awk {'print $4'}`
        if [[ $fileName != "" ]]
          then
            printf 'Deleting "%s"\n' $fileName
            s3cmd del "$fileName"
        fi
    fi
  done;
}

for dir in ${LISTDIR[*]}
do
   find $SRCDIR$dir -mtime +10 -type f -delete
   remove_s3 $S3NAME"/static/"$dir "10 days"
done