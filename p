#!/bin/bash
source ~/.profile-pugs

INSTANCE='i-43936f16'
MNT=pycon
KEYFILE=~/doc/keys/pugs.pem
POSTGRES_BIN=/opt/local/lib/postgresql84/bin
POSTGRES_DATA=/opt/local/var/db/postgresql84/defaultdb
POSTGIS_CONTRIB=/opt/local/share/postgresql84/contrib/postgis-1.5
DBNAME=pycon
DBUSER=pycon
DBADMIN=postgres
TMPFILE=/tmp/ec2-describe-instances-pycon
ARGS=`getopt --long start,stop,mount,unmount,tunnel,serve,shell -- x $@`

if [ $? != 0 ]
then
	echo "Usage: $0 --[start|stop|mount|unmount|tunnel|dbstart|dbstop|createdb|dropdb|resetdbdbshell|dbshelladmin|serve|shell]" >&2
	exit 1
fi

set -- $ARGS

if [ $# != 2 ]
then
	echo "Usage: $0 --[start|stop|mount|unmount|tunnel|serve]" >&2
	exit 1
fi

function _ec2_data() {
	if [ ! -a $TMPFILE ]; then
		ec2-describe-instances $INSTANCE > $TMPFILE
	fi
}

for i
do
        case "$i"
	in
                --start)
			echo "Starting instance ..."
			ec2-start-instances $INSTANCE
			exit 0
			;;
                --stop)
			echo "Stopping instance ..."
			ec2-stop-instances $INSTANCE
			exit 0
			;;
		--mount)
			_ec2_data
			echo 'Mounting ...'
			if [ -d /Volumes/$MNT/repo ]
			then
				echo 'Already mounted...'
				exit 0
			fi

			IP=`cat $TMPFILE | grep ^INSTANCE | awk '{ print $4 }'`

			mkdir -p /Volumes/$MNT
			sshfs ubuntu@$IP: /Volumes/$MNT -o IdentityFile=$KEYFILE
			exit 0
			;;
		--unmount)
			echo 'Unmounting ..'
			if [ -d /Volumes/$MNT/repo ]; then
				umount /Volumes/$MNT
			fi
			exit 0
			;;
		--tunnel)
			_ec2_data
			IP=`cat $TMPFILE | grep ^INSTANCE | awk '{ print $4 }'`
			ssh -L localhost:8080:localhost:80 -i $KEYFILE ubuntu@$IP
			exit 0
			;;
		--serve)
			cd $VIRTUAL_ENV/web2py
			python web2py.py -a admin
			exit 0
			;;
		--shell)
			cd $VIRTUAL_ENV/web2py
			python web2py.py -S pycon -M
			exit 0
			;;
                --)
			shift; break;;
                *) echo "Internal error!"; exit 1;;
        esac
done
