"""Custom error pages (400 / 403 / 404 / 500 and CSRF failures).

Every handler renders the same template with fixed, friendly text and the
correct HTTP status code. Nothing from the exception, the URL, or the
request is ever put on the page, so no internal details can leak.
"""
from django.http import Http404, HttpResponse
from django.template import loader

ERRORS = {
    400: (
        "Bad request",
        "Something about that request didn't look right. "
        "Please go back and try again.",
    ),
    403: (
        "Access denied",
        "You don't have permission to view this page. If you think this is "
        "a mistake, please head back and try again.",
    ),
    404: (
        "Page not found",
        "We couldn't find the page you were looking for. The link may be "
        "wrong or the page may have moved.",
    ),
    500: (
        "Something went wrong",
        "It's not you, it's us. We've hit an unexpected problem. "
        "Please try again in a few minutes.",
    ),
}


def _render_error(status):
    title, message = ERRORS[status]
    context = {
        "status_code": status,
        "error_title": title,
        "error_message": message,
    }
    try:
        # No `request` on purpose: skips context processors (session, DB,
        # messages), so this can still render when the app itself is broken.
        body = loader.render_to_string("barbershop/error.html", context)
    except Exception:
        # Last resort if even the template fails: plain, static, safe HTML.
        body = (
            "<!doctype html><meta charset='utf-8'>"
            f"<title>{status} - {title}</title>"
            f"<h1>{status}</h1><p>{title}</p><p><a href='/'>Back to home</a></p>"
        )
    return HttpResponse(body, status=status)


def bad_request(request, exception=None):
    return _render_error(400)


def permission_denied(request, exception=None):
    return _render_error(403)


def page_not_found(request, exception=None):
    return _render_error(404)


def server_error(request):
    return _render_error(500)


def csrf_failure(request, reason=""):
    """Expired or missing CSRF token. `reason` is deliberately not shown."""
    return _render_error(403)


def preview(request, code):
    """DEBUG-only helper so you can see each page while DEBUG=True
    (Django's own technical 404 otherwise hides the custom handler)."""
    if code not in ERRORS:
        raise Http404
    return _render_error(code)
