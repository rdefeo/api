__author__ = 'robdefeo'
import os


def get_env_setting(env_variable_name, default):
    if env_variable_name in os.environ:
        return os.environ[env_variable_name]
    else:
        return default


PORT = int(get_env_setting("API_PORT", 9999))

# MONGODB_PASSWORD = get_env_setting("DETECT_MONGODB_PASSWORD", "jemboo")
DETECT_URL = get_env_setting("API_DETECT_URL", "http://0.0.0.0:18999")
SUGGEST_URL = get_env_setting("API_SUGGEST_URL", "http://0.0.0.0:14999")
CONTEXT_URL = get_env_setting("API_CONTEXT_URL", "http://0.0.0.0:17999")
