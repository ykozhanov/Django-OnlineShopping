import logging
from urllib.parse import urlparse, parse_qs, urlencode

from django import template

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def update_request_params(value, key, request_params):
    """Обновление request_params"""
    if value == "asc":
        new_value = "desc"
    elif value == "desc":
        new_value = ""
    else:
        new_value = "asc"
    parsed_url = urlparse(request_params)
    path_params = parse_qs(parsed_url.path)
    if new_value != "":
        path_params[key] = [new_value]
    elif key in path_params:
        del path_params[key]
    if not path_params:
        updated_request_params = ""
    else:
        updated_request_params = "&" + urlencode(path_params, doseq=True)

    return updated_request_params
