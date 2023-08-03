"""https://github.com/HackSoftware/Django-Styleguide-Example/"""
from os import getenv

from dotenv import find_dotenv, load_dotenv

from django.urls import include, path

load_dotenv(find_dotenv())


def show_toolbar() -> bool:
    """
    """
    DEBUG = getenv("DJANGO_DEBUG", "0") == "1"
    if not DEBUG:
        return False

    try:
        import debug_toolbar
    except ImportError:
        return False

    return True


class DebugToolbarSetup:
    """
    """
    @staticmethod
    def do_settings(INSTALLED_APPS, MIDDLEWARE, middleware_position=None):
        _show_toolbar: bool = show_toolbar()

        if not _show_toolbar:
            return INSTALLED_APPS, MIDDLEWARE

        INSTALLED_APPS = INSTALLED_APPS + ["debug_toolbar"]

        debug_toolbar_middleware = "debug_toolbar.middleware.DebugToolbarMiddleware"

        if middleware_position is None:
            MIDDLEWARE = MIDDLEWARE + [debug_toolbar_middleware]
        else:
            # Grab a new copy of the list, since insert mutates the internal structure
            _middleware = MIDDLEWARE[::]
            _middleware.insert(middleware_position, debug_toolbar_middleware)

            MIDDLEWARE = _middleware

        return INSTALLED_APPS, MIDDLEWARE

    @staticmethod
    def do_urls(urlpatterns):
        if not show_toolbar():
            return urlpatterns

        import debug_toolbar

        return urlpatterns + [path("__debug__/", include(debug_toolbar.urls))]
