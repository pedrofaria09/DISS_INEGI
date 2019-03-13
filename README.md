# Dissertation - INEGI

## Getting Started

These instructions will get project running on your local machine for development and testing purposes.

### Prerequisites

Applications necessary to make instalation possible:

* [Docker](https://www.docker.com/) - A container software

### Installing and Running

A step by step series of examples that tell you how to get a development env running

Change 'HOST' from DATABASES in settings.py to:
```
'HOST': 'postgres',
```

Change InfluxDB connection in views.py to:
```
myclient = InfluxDBClient(host='influx', port=8086, database='INEGI_INFLUX')
```

Change MongoDB connection in models.py to:
```
connect(db='INEGI', host='mongo')
```

Install dependencies:
```
docker build .
```

Create a superuser (necessary to do a login in the web app):
```
docker-compose run web python manage.py createsuperuser
```

Run docker:
```
docker-compose up
```

Access at:
```
http://localhost:8000/
```
