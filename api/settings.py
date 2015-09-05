import logging

__author__ = 'robdefeo'
import os


def get_env_setting(env_variable_name, default):
    if env_variable_name in os.environ:
        return os.environ[env_variable_name]
    else:
        return default


PORT = int(get_env_setting("API_PORT", 9999))

ADD_DEV_SSL = bool(int(get_env_setting("ADD_DEV_SSL", 0)))

ADD_CORS_HEADERS = bool(int(get_env_setting("ADD_CORS_HEADERS", 0)))

DETECT_URL = get_env_setting("API_DETECT_URL", "http://0.0.0.0:18999")
SUGGEST_URL = get_env_setting("API_SUGGEST_URL", "http://0.0.0.0:14999")
CONTEXT_URL = get_env_setting("API_CONTEXT_URL", "http://0.0.0.0:17999")
CONTENT_URL = get_env_setting("API_CONTENT_URL", "http://content.jemboo.com")

CONTENT_CACHE_SIZE = int(get_env_setting("API_CONTENT_CACHE_SIZE", 4096))

LOGGING_LEVEL = logging.DEBUG
