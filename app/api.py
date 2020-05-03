from datetime import datetime
from flask import Blueprint, abort, jsonify, request, current_app

from .auth import AuthError, requires_auth
from .models import Movie, Actor

api = Blueprint('api', __name__)


@api.route('/')
def index():
    msg = 'Casting Agency API'
    return jsonify(msg)


@api.route('/movies', methods=["GET"])
@requires_auth('get:movies')
def get_movies(payload):
    movies = Movie.query.order_by(Movie.id).all()

    if len(movies) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "movies": [movie.format() for movie in movies]
    })


@api.route('/movies', methods=["POST"])
@requires_auth('post:movies')
def post_movies(payload):
    body = request.get_json()

    if body is None:
        abort(400)

    title = body.get('title', None)
    release_date = body.get('release_date', None)
    actors = body.get('actors', None)

    try:
        movie = Movie(title=title, release_date=datetime.strptime(
            release_date, '%Y-%m-%d'))

        if actors:
            movie.actors = Actor.query.filter(Actor.id.in_(actors)).all()

        movie.insert()

        return jsonify({
            "success": True,
            "movie": movie.format()
        })
    except Exception as e:
        current_app.logger.error(e)
        abort(422)


@api.route('/movies/<int:movie_id>', methods=["PATCH"])
@requires_auth('patch:movies')
def patch_movies(payload, movie_id):
    body = request.get_json()

    if body is None:
        abort(400)

    movie = Movie.query.get(movie_id)

    title = body.get('title', None)
    release_date = body.get('release_date', None)
    actors = body.get('actors', None)

    if movie is None:
        abort(404)

    try:
        movie.title = title

        if release_date:
            movie.release_date = datetime.strptime(
                release_date, '%Y-%m-%d')

        if actors:
            movie.actors = actors

        movie.update()

        return jsonify({
            "success": True,
            "movie": movie.format()
        })
    except Exception as e:
        current_app.logger.error(e)
        abort(422)


@api.route('/movies/<int:movie_id>', methods=["DELETE"])
@requires_auth('delete:movies')
def delete_movie(payload, movie_id):
    movie = Movie.query.get(movie_id)

    if movie is None:
        abort(404)

    try:
        movie.delete()

        movies = Movie.query.order_by(Movie.id).all()

        return jsonify({
            "success": True,
            "deleted": movie_id
        })
    except Exception as e:
        current_app.logger.error(e)
        abort(422)


@api.route('/actors')
@requires_auth('get:actors')
def get_actors(payload):
    actors = Actor.query.order_by(Actor.id).all()

    if actors == []:
        abort(404)

    return jsonify({
        "success": True,
        "actors": [actor.format() for actor in actors]
    })


@api.route('/actors', methods=["POST"])
@requires_auth('post:actors')
def create_actor(payload):
    body = request.get_json()

    if body is None:
        abort(400)

    name = body.get('name', None)
    gender = body.get('gender', None)
    age = body.get('age', None)

    try:
        actor = Actor(name=name, gender=gender, age=age)

        actor.insert()

        return jsonify({
            "success": True,
            "actor": actor.format()
        })
    except Exception as e:
        current_app.logger.error(e)
        abort(422)


@api.route('/actors/<int:actor_id>', methods=["PATCH"])
@requires_auth('patch:actors')
def edit_actor(payload, actor_id):
    actor = Actor.query.get(actor_id)

    if actor is None:
        abort(404)

    body = request.get_json()

    try:
        actor.name = body.get('name', None)
        actor.gender = body.get('gender', None)
        actor.age = body.get('age', None)

        actor.update()

        return jsonify({
            "success": True,
            "actor": actor.format()
        })
    except Exception as e:
        current_app.logger.error(e)
        abort(422)


@api.route('/actors/<int:actor_id>', methods=["DELETE"])
@requires_auth('delete:actors')
def delete_actor(payload, actor_id):
    actor = Actor.query.get(actor_id)

    if actor is None:
        abort(404)

    try:
        actor.delete()

        actors = Actor.query.order_by(Actor.id).all()

        return jsonify({
            "success": True,
            "deleted": actor_id
        })
    except Exception as e:
        current_app.logger.error(e)
        abort(422)


@api.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        'success': False,
        "error": 404,
        "message": "Resource was not found"
    }), 404


@api.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        'success': False,
        "error": 422,
        "message": "Unprocessable Entity"
    }), 422


@api.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        "error": 400,
        "message": "Bad request"
    }), 400


@api.errorhandler(405)
def method_not_found(error):
    return jsonify({
        'success': False,
        "error": 405,
        "message": "Method not found"
    }), 405


@api.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        "error": 500,
        "message": "Internal Server error"
    }), 500


@api.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
