# Dissertation - INEGI

## Getting Started

These instructions will get project running on your local machine for development and testing purposes.

### Prerequisites

Applications necessary to make instalation possible:

* [Docker](https://www.docker.com/) - A container software

### Installing and Running

A step by step on how to get a development env running

Change flag DOCKER to True in settings.py (Line 31) to:
```
DOCKER = True
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
