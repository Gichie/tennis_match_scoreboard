from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
import os
import mimetypes

from src.controllers.application_controller import (
    handle_index,
    handle_new_match,
    handle_match_score
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Application:
    def __init__(self):
        self.url_map = Map([
            Rule("/", endpoint="index"),
            Rule("/new_match", endpoint="new_match", methods=["POST"]),
            Rule("/match_score", endpoint="match_score"),
            Rule("/static/<path:filename>", endpoint="static")  # Маршрут для статических файлов
        ])

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        adapter = self.url_map.bind_to_environ(environ)

        try:
            endpoint, values = adapter.match()
            if endpoint == "index":
                response = handle_index(request)
            elif endpoint == "new_match":
                response = handle_new_match(request)
            elif endpoint == "match_score":
                response = handle_match_score(request)
            elif endpoint == "static":
                return self.serve_static(request, **values)
            else:
                response = Response("Not Found", status=404)
        except Exception as e:
            response = Response(f"Error: {str(e)}", status=500)

        return response(environ, start_response)

    def serve_static(self, request, filename):
        """Раздача статических файлов"""
        static_path = os.path.join(BASE_DIR, "static")
        return SharedDataMiddleware(lambda env, sr: Response("404 Not Found", status=404),
                                    {"/static": static_path})(request.environ, request.start_response)

    def handle_index(self, request):
        return handle_index(request)

    def handle_new_match(self, request):
        return handle_new_match(request)

    def handle_match_score(self, request):
        return handle_match_score(request)



def create_app():
    return Application()
