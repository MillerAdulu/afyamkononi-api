"""Web Routes."""

from masonite.routes import Get, Post, RouteGroup

ROUTES = [
    Get('/', 'WelcomeController@show').name('welcome'),

    RouteGroup([
        RouteGroup([
            Post('/', 'RegisterController@store'),
        ], prefix="/accounts")
    ], prefix="/api")
]
