#! /usr/bin/bash

Aknowladgment="[RUNNING] run.sh Script is running..."
echo "${Aknowladgment}"

CurrentOSType=$(uname)
echo "[INFO] You are Running $CurrentOSType"




if [ "$CurrentOSType" == "Linux" ]
then 


    xterm -hold -e "redis-server" & sleep 3
    xterm -hold -e "celery -A project worker -l INFO"& sleep 2

    xterm -hold -e "python3 manage.py runserver $1"



elif [ "$CurrentOSType" == "Darwin" ] 
then echo "Hmm...Mac it's"
    xterm -hold -e "redis-server" & sleep 2
    xterm -hold -e "celery -A project worker -l INFO" & sleep 1
    xterm -hold -e "python manage.py runserver" &

fi

echo "[STOPPED] run.sh Script is Stopped."