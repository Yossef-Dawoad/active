#! /usr/bin/bash

Aknowladgment="[RUNNING] run.sh Script is running..."
echo "${Aknowladgment}"

CurrentOSType=$(uname)
echo "[INFO] You are Running $CurrentOSType"

if [ "$1" == '' ]
then 
    redis_CMD="redis-server"
    server_CMD="python3 manage.py runserver" 
else
    redis_CMD="redis-cli -h $1 -p 6379"
    server_CMD="python3 manage.py runserver '$1':'$2'"
fi



if [ "$CurrentOSType" == "Linux" ]
then 

    xterm -hold -e "${redis_CMD}" & sleep 3
    xterm -hold -e "python3 -m celery -A project worker -l INFO"& sleep 4
    xterm -hold -e "${server_CMD}"



elif [ "$CurrentOSType" == "Darwin" ] 
then echo "Hmm...Mac it's"
    xterm -hold -e "redis-server" & sleep 2
    xterm -hold -e "python3 -m celery -A project worker -l INFO" & sleep 1
    xterm -hold -e "python3 manage.py runserver" &

fi

echo "[STOPPED] run.sh Script is Stopped."