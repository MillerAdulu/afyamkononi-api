"""Web Routes."""

from masonite.routes import Get, Post, RouteGroup

ROUTES = [
    Get('/', 'WelcomeController@show').name('welcome'),

    RouteGroup([
        RouteGroup([
            Get('/@user', 'RegisterController@show'),
            Post('/', 'RegisterController@store'),
        ], prefix="/accounts")
    ], prefix="/api")
]
