"""Web Routes."""

from masonite.routes import Get, Post, RouteGroup

ROUTES = [
    Get('/', 'WelcomeController@show').name('welcome'),

    RouteGroup([
        RouteGroup([
            Get('/@user', 'AuthController@view_user'),
            Post('/', 'AuthController@register'),
        ], prefix="/accounts")
    ], prefix="/api")
]
