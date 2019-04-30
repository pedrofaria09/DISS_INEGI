# Dissertation - INEGI

## Getting Started

These instructions will get project running on your local machine for development and testing purposes.

### Prerequisites

Applications necessary to make instalation possible:

* [Docker](https://www.docker.com/) - A container software

### Installing and Running

A step by step on how to get a development env running

Change flag DOCKER from False to True in settings.py (Line 31):
```
DOCKER = True
```

Install dependencies:
```
docker build .
```

Run docker:
```
docker-compose up
```

If 1st time, need to create a superuser:
```
docker-compose run web python manage.py createsuperuser
```

Access at:
```
http://localhost:8000/
```


## Backup and restore database

Using package django-dbbackup, gives the user to backup and restore the database

To backup:
```
docker-compose run web python manage.py dbbackup
```
A backup file will be created at: files/backup

To restore:
```
docker-compose run web python manage.py dbrestore
```
