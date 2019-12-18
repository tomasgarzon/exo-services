#!/bin/sh
# this script must be placed in /etc/cron.daily/disk_alert.sh
ADMIN="devops@openexo.com"
ALERT=85
df -PkH | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 " " $6 }' | while read output;
do
  usep=$(echo $output | awk '{ print $1}' | cut -d'%' -f1 )
  partition=$(echo $output | awk '{print $2}' )
  if [ $usep -ge $ALERT ]; then
    echo "Running out of space \"$partition ($usep%)\" on $(hostname) as on $(date)" |
    mail -s "[AWS]: $(hostname) almost out of disk space $usep%" $ADMIN
  fi
done