

from django.http import HttpRequest


class SaveSessionKeyMiddleware:
    """Необходим для сохранения идентификатора сессии до авторизации.
    Django автоматически изменяет идентификатор после авторизации"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if hasattr(request, 'session') and request.session.session_key:
            request._pre_auth_session_key = request.session.session_key
        response = self.get_response(request)
        return response
