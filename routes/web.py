"""Web Routes."""

from masonite.routes import Get, Post, Patch, RouteGroup

ROUTES = [
    Get("/", "WelcomeController@show").name("welcome"),
    RouteGroup(
        [
            RouteGroup(
                [
                    Post("/sign_in", "AuthController@sign_in"),
                    Patch("/seed_admin", "AuthController@seed_admin"),
                ],
                prefix="/auth",
            ),
            RouteGroup(
                [
                    Get("/@user", "AccountController@view_user"),
                    Post("/", "AccountController@register"),
                ],
                prefix="/accounts",
                middleware=("auth"),
            ),
            RouteGroup(
                [
                    Patch("/@patient_id", "PatientRecordsController@store"),
                    Get("/@patient_id", "PatientRecordsController@show"),
                ],
                prefix="/records",
                middleware=("auth"),
            ),
        ],
        prefix="/api",
    ),
]
