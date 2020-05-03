# UDACITY FULLSTACK-DEVELOPER NANODEGREE CAPSTONE PROJECT

This projects provides an API backend for a casting application with CRUD actions for movies and actors and simply manage actors assigned to movies

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/` directory and running:

```bash
pip install -r requirements.txt
```

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## API Reference

### Getting Started

- Base URL: Currently this application is only hosted locally. The backend is hosted at `http://127.0.0.1:5000/`
- Authentication: Authentication is based on JWT Tokens with role based authentication.

### Roles
- Casting assistant: A casting assistang can view actors and movies
- Casting director: A casting director extends the casting assistant's permissions by adding and deleting actors from the database and can also change actors and movies
- Executive Producer: The executive producer extends the casting director's permissions by adding or deleting movies from the database

### Error Handling
Errors are returned as JSON in the following format:
```json
{
    "success": false,
    "error": 404,
    "message": "Resource not found"
}
```

The API will return two types of errors:

- 404 – Resource not found
- 422 – Unprocessable Entity
- 400 - Bad request
- 405 - Method not found
- 500 - Internal Server error
- 401 - Unauthorized
- 4ß3 - Forbidden

### Endpoints

#### `GET /api/v1/movies`
> Returns a list of movies
```json
{
    "success": true,
    "movies": [
        {
            "actors": [], 
            "id": 1, 
            "release_date": "Tue, 04 Dec 2012 00:00:00 GMT", 
            "title": "Title"
        },
        {
            "actors": [1], 
            "id": 2, 
            "release_date": "Tue, 04 Dec 2012 00:00:00 GMT", 
            "title": "Title2"
        }
    ]
}
```

#### `POST /api/v1/movies`
> Returns a list of movies
```json
{
    "success": true,
    "movie": {
        "actors": [], 
        "id": 1, 
        "release_date": "Tue, 04 Dec 2012 00:00:00 GMT", 
        "title": "Title"
    }
}
```

#### `PATCH /api/v1/movies`
> Returns a list of movies
```json
{
    "success": true,
     "movie": {
        "actors": [], 
        "id": 1, 
        "release_date": "Tue, 04 Dec 2012 00:00:00 GMT", 
        "title": "Title"
    }
}
```

#### `DELETE /api/v1/movies/<int:movie_id>`
> Deletes a movie by id
```json
{
    "success": true,
    "deleted": 12
}
```

#### `GET /api/v1/actors`
> Returns a list of actors
```json
{
    "success": true,
    "actors": [
        {
            "age": 30, 
            "gender": "male", 
            "id": 1, 
            "name": "Name"
        },
        {
            "age": 50, 
            "gender": "male", 
            "id": 1, 
            "name": "Name2"
        }
    ]
}
```

#### `POST /api/v1/actors`
> Returns a list of actors
```json
{
    "success": true,
    "actor": {
        "age": 30, 
        "gender": "male", 
        "id": 1, 
        "name": "Name"
    }
}
```

#### `PATCH /api/v1/actors`
> Returns a list of actors
```json
{
    "success": true,
    "actor": {
        "age": 30, 
        "gender": "male", 
        "id": 1, 
        "name": "Name"
    }
}
```

#### `DELETE /api/v1/actors/<int:actors_id>`
> Deletes a actor by id
```json
{
    "success": true,
    "deleted": 12
}
```

## Running tests

Tests are prefixed with numbers to sort their test execution

Script for running tests:

```bash
python test_app.py
```

## Hosting

The application is hosted by heroku under the url: ['heroku app'](https://casting0815.herokuapp.com/api/v1/)
