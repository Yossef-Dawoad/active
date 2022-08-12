# active



## Installation
- you have to install on your machine:
  - python 3
  - Redis  
  - ffmpeg
  
you can run the following to make sure that they are installed 
```bash
python --version
```

```bash
redis-server --version
```
**Note** 
in Linux you need to configure `redis.conf` file if you wan to allow remote connection  
in `sudo nano /etc/redis/redis.conf` set 
```bash
supervised sysmd
bind 0.0.0.0
```
and then restart the service by running 
```
sudo systemctl restart redis.service
```
after you make sure they are installed 
run the following command to install all required libraries you need  
`**Note** run the command in the repo Directory`
```bash
pip install -r requirements.txt
```

you also have to create `.env` file in `active/project` and write inside
```
mailsender=<youremail>@gmail.com
senderpasscode=<gmail applicaton password>
secretkey=<your django-secret key>
```

## Run the Project 
you can either run it with single command `experimental LINUX only`
```bash
./run.sh
```
or you can write the following in `**3 different terminals**`   
**Note Order matter**
```bash
python manage.py makemigraton
python manage.py migrate
```
```bash
python manage.py createsuperuser
```
```bash
redis-server
```
```bash
celery -A project worker -l INFO
```

```bash
python manage.py runserver
```
