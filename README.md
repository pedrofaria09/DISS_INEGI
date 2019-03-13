# Dissertation - INEGI

## Getting Started

These instructions will get project running on your local machine for development and testing purposes.

### Prerequisites

Applications necessary to make instalation possible:

* [Docker](https://www.docker.com/) - A container software

### Installing

A step by step series of examples that tell you how to get a development env running

Change 'HOST' from DATABASES in settings.py to:
```
'HOST': 'db_pg',
```
Change INFLUX connection in models.py to:
```
myclient = InfluxDBClient(host='db_in', port=8086, database='INEGI_INFLUX')
```

Install dependencies:
```
docker build .
```

Run docker:
```
docker-compose up
```

If need to create superuser (To do login):
```
docker-compose run web python manage.py createsuperuser
```
