"""Middleware Configuration Settings."""

from masonite.middleware import CorsMiddleware, ResponseMiddleware, MaintenanceModeMiddleware

from app.http.middleware.AuthenticationMiddleware import \
    AuthenticationMiddleware
from app.http.middleware.CsrfMiddleware import CsrfMiddleware
from app.http.middleware.LoadUserMiddleware import LoadUserMiddleware
from app.http.middleware.VerifyEmailMiddleware import VerifyEmailMiddleware

"""HTTP Middleware
HTTP middleware is middleware that will be ran on every request. Middleware
is only ran when a HTTP call is successful (a 200 response). This list
should contain a simple aggregate of middleware classes.
"""

HTTP_MIDDLEWARE = [
    LoadUserMiddleware,
    CsrfMiddleware,
    ResponseMiddleware,
    MaintenanceModeMiddleware,
]

CORS = {
    'Access-Control-Allow-Origin': "*",
    "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
    "Access-Control-Allow-Headers": "Content-Type, Accept, X-Requested-With",
    "Access-Control-Max-Age": "3600",
    "Access-Control-Allow-Credentials": "true"
}

"""Route Middleware
Specify a dictionary of middleware to be used on a per route basis here. The key will
be the alias to use on routes and the value can be any middleware class or a list
of middleware (middleware stacks).
"""

ROUTE_MIDDLEWARE = {
    'auth': AuthenticationMiddleware,
    'verified': VerifyEmailMiddleware,
}
