# active



## Installation
- you have to install on your machine:
  - python 3
  - Redis 
you can run the following to make sure that they are installed 
```bash
python --version
```

```bash
redis-server --version
```
after you make sure they are installed 
run the following command to install all required libraries you need  
`**Note** run the command in the repo Directory`
```bash
pip install -r requirements.txt
```

## Run the Project 
you can either run it with single command `experimental LINUX only`
```bash
./run.sh
```
or you can write the following in `**3 different terminals**`   
**Note Order matter**

```bash
redis-server
```
```bash
celery -A project worker -l INFO
```

```bash
python manage.py runserver
```