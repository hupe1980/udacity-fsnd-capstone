import json
from functools import wraps
from datetime import datetime
from mock import patch
import unittest
from flask import request, abort

from app.models import Movie, Actor
from app import create_app, db

API_PREFIX = '/api/v1'

ROLES = {
    "CASTING_ASSISTANT": {
        "permissions": [
            "get:movies",
            "get:actors"
        ]
    },
    "CASTING_DIRECTOR": {
        "permissions": [
            "get:movies",
            "get:actors",
            "post:actors",
            "delete:actors",
            "patch:movies",
            "patch:actors"
        ]
    },
    "EXECUTIVE_PRODUCER": {
        "permissions": [
            "get:movies",
            "get:actors",
            "post:actors",
            "delete:actors",
            "patch:movies",
            "patch:actors",
            "post:movies",
            "delete:movies"
        ]
    }
}


def mock_requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            role_name = request.headers.get("ROLE", None)

            if role_name is None:
                raise AuthError({
                    'code': 'auth_header_missing',
                    'description': 'Authorization header is expected'
                }, 401)

            payload = {
                "permissions": ROLES[role_name]["permissions"]
            }

            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


patch('app.auth.requires_auth', mock_requires_auth).start()

from app.auth import check_permissions, AuthError  # noqa


class CastingTestCase(unittest.TestCase):
    """This class represents the casting test case"""

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.new_movie = {'title': 'Title', 'release_date': '2012-12-04'}

        self.update_movie = {'title': 'Patched_Title',
                             'release_date': '2012-12-04'}

        self.invalid_movie = {'release_date': '2012-12-04'}

        self.new_actor = {'name': 'Name', 'age': 30, 'gender': 'male'}

        self.update_actor = {'name': 'Patched_Name',
                             'age': 30, 'gender': 'male'}

        self.invalid_actor = {'age': 30, 'gender': 'male'}

    def tearDown(self):
        """Executed after reach test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_movies(self):
        movie = Movie(title='Test')
        movie.insert()

        res = self.client().get(
            f'{API_PREFIX}/movies', headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movies'], [movie.format()])

    def test_get_movies_404(self):
        res = self.client().get(f'{API_PREFIX}/movies',
                                headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")

    def test_get_movies_401(self):
        res = self.client().get(f'{API_PREFIX}/movies')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected")

    def test_post_movies(self):
        res = self.client().post(f'{API_PREFIX}/movies', json=self.new_movie,
                                 headers={"ROLE": "EXECUTIVE_PRODUCER"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(self.new_movie['title'], data['movie']['title'])

    def test_post_movies_422(self):
        res = self.client().post(f'{API_PREFIX}/movies',
                                 json=self.invalid_movie,
                                 headers={"ROLE": "EXECUTIVE_PRODUCER"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_movies_401(self):
        res = self.client().post(f'{API_PREFIX}/movies', json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected")

    def test_post_movies_403(self):
        res = self.client().post(f'{API_PREFIX}/movies', json=self.new_movie,
                                 headers={"ROLE": "CASTING_DIRECTOR"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Forbidden")

    def test_patch_movies(self):
        movie = Movie(title='Test')

        movie.insert()

        res = self.client().patch(f'{API_PREFIX}/movies/{movie.id}',
                                  json=self.update_movie,
                                  headers={"ROLE": "CASTING_DIRECTOR"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(self.update_movie['title'], data['movie']['title'])

    def test_patch_movies_401(self):
        res = self.client().patch(
            f'{API_PREFIX}/movies/9999', json=self.update_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected")

    def test_patch_movies_403(self):
        res = self.client().patch(f'{API_PREFIX}/movies/9999',
                                  json=self.update_movie,
                                  headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Forbidden")

    def test_patch_movies_404(self):
        res = self.client().patch(f'{API_PREFIX}/movies/9999',
                                  json=self.update_movie,
                                  headers={"ROLE": "CASTING_DIRECTOR"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")

    def test_delete_movies(self):
        movie = Movie(title='Test')

        movie.insert()

        res = self.client().delete(
            f'{API_PREFIX}/movies/{movie.id}',
            headers={"ROLE": "EXECUTIVE_PRODUCER"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], movie.id)

    def test_delete_movies_401(self):
        res = self.client().delete(f'{API_PREFIX}/movies/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected")

    def test_delete_movies_403(self):
        res = self.client().delete(
            f'{API_PREFIX}/movies/9999', headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Forbidden")

    def test_delete_movies_404(self):
        res = self.client().delete(
            f'{API_PREFIX}/movies/9999',
            headers={"ROLE": "EXECUTIVE_PRODUCER"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")

    def test_get_actors(self):
        actor = Actor(name='Test')
        actor.insert()

        res = self.client().get(
            f'{API_PREFIX}/actors',
            headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actors'], [actor.format()])

    def test_get_actors_404(self):
        res = self.client().get(f'{API_PREFIX}/actors',
                                headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")

    def test_get_actors_401(self):
        res = self.client().get(f'{API_PREFIX}/actors')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected")

    def test_post_actors(self):
        res = self.client().post(f'{API_PREFIX}/actors',
                                 json=self.new_actor,
                                 headers={"ROLE": "EXECUTIVE_PRODUCER"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(self.new_actor['name'], data['actor']['name'])

    def test_post_actors_422(self):
        res = self.client().post(f'{API_PREFIX}/actors',
                                 json=self.invalid_actor,
                                 headers={"ROLE": "EXECUTIVE_PRODUCER"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_actors_401(self):
        res = self.client().post(f'{API_PREFIX}/actors',
                                 json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected")

    def test_post_actors_403(self):
        res = self.client().post(f'{API_PREFIX}/actors',
                                 json=self.new_actor,
                                 headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Forbidden")

    def test_patch_actors(self):
        actor = Actor(name='Test')

        actor.insert()

        res = self.client().patch(f'{API_PREFIX}/actors/{actor.id}',
                                  json=self.update_actor,
                                  headers={"ROLE": "CASTING_DIRECTOR"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            self.update_actor['name'], data['actor']['name'])

    def test_patch_actors_401(self):
        res = self.client().patch(
            f'{API_PREFIX}/actors/9999', json=self.update_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected")

    def test_patch_actors_403(self):
        res = self.client().patch(f'{API_PREFIX}/actors/9999',
                                  json=self.update_actor,
                                  headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Forbidden")

    def test_patch_actors_404(self):
        res = self.client().patch(f'{API_PREFIX}/actors/9999',
                                  json=self.update_actor,
                                  headers={"ROLE": "CASTING_DIRECTOR"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")

    def test_delete_actors(self):
        actor = Actor(name='Test')

        actor.insert()

        res = self.client().delete(
            f'{API_PREFIX}/actors/{actor.id}',
            headers={"ROLE": "CASTING_DIRECTOR"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], actor.id)

    def test_delete_actors_401(self):
        res = self.client().delete(f'{API_PREFIX}/actors/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Authorization header is expected")

    def test_delete_actors_403(self):
        res = self.client().delete(
            f'{API_PREFIX}/actors/9999', headers={"ROLE": "CASTING_ASSISTANT"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Forbidden")

    def test_delete_actors_404(self):
        res = self.client().delete(
            f'{API_PREFIX}/actors/9999', headers={"ROLE": "CASTING_DIRECTOR"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource was not found")


if __name__ == "__main__":
    unittest.main()
