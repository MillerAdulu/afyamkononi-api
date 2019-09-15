"""Web Routes."""

from masonite.routes import Get, Post, Patch, RouteGroup

ROUTES = [
    Get("/", "WelcomeController@show").name("welcome"),
    RouteGroup(
        [
            RouteGroup(
                [
                    Get("/@user", "AuthController@view_user"),
                    Post("/", "AuthController@register"),
                    Post("/sign_in", "AuthController@sign_in"),
                    Patch('/seed_admin', "AuthController@seed_admin")
                ],
                prefix="/accounts",
            )
        ],
        prefix="/api",
    ),
]
