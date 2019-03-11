# Dissertation - INEGI

## Getting Started

These instructions will get project running on your local machine for development and testing purposes.

### Prerequisites

Applications necessary to make instalation possible:

* [Docker](https://www.docker.com/) - A container software

### Installing

A step by step series of examples that tell you how to get a development env running

1st - Change 'HOST' from DATABASES in settings.py to:
```
'HOST': 'db_pg',
```

2nd - Install dependencies:
```
docker build .
```

3rd - Run docker:
```
docker-compose up
```

If need to create superuser (To do login):
```
docker-compose run web python manage.py createsuperuser
```