#!/bin/bash
#
# Nagios Filesystem Plugin
#
# Description: Check the filesystem status
# Author     : Stephane Beuret
# Version    : 1.0
#
#

# Usage
if [ $# -lt 2 ]; then
echo "Usage: $0 <warning> <critical>"
exit 2
fi

# Filesystem threshold values
Filesystem_WARNING=$1
Filesystem_CRITICAL=$2

if (( $Filesystem_CRITICAL <= $Filesystem_WARNING ))
then
        echo "Critical value must be less than the warning value"
        exit 5
fi

# Output for the dashboard
ALARMS=0
for i in `df -k|grep ^/|grep -v devices|grep -v cdrom|grep -v proc|awk '{print int($3*100/$2)}'`
do
if [ $i -ge $Filesystem_WARNING ] ; then ALARMS=$(( ALARMS + 1 )); fi
done

RESULT="echo `df -k|grep ^/|grep -v devices|grep -v cdrom|grep -v proc|awk '{if (int($3*100/$2) < 10) {print " - 0"int($3*100/$2) "% full on "$6" Free space left: "int($4/1024)" MB"} else {print " - "int($3*100/$2) "% full on "$6" Free space left: "int($4/1024)" MB"}}'|sort -r|head -$ALARMS`"
MYRESULT=`$RESULT`

for i in `df -k|grep ^/|grep -v devices|grep -v cdrom|grep -v proc|awk '{if (int($3*100/$2) < 10) {print 0int($3*100/$2)} else {print int($3*100/$2)}}'|sort -r`
  do
    if [ $i -lt $1 ] ; then
	echo "DISK OK" ; exit 0

    elif [ $i -ge $2 ] ; then
	echo "DISK CRITICAL $MYRESULT" ; exit 2

    else
	echo "DISK WARNING $MYRESULT" ; exit 1
    fi
  done
