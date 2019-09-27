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
                    Get("/@user", "AccountController@user_by_id"),
                    Get("/gov_id/@user", "AccountController@user_by_gov_id"),
                    Post("/", "AccountController@register"),
                ],
                prefix="/accounts",
                middleware=("auth",),
            ),
            RouteGroup(
                [
                    Patch("/@patient_id", "PatientRecordsController@store"),
                    Get("/@patient_id", "PatientRecordsController@show"),
                    Get("/", "PatientRecordsController@index"),
                ],
                middleware=("auth",),
                prefix="/records",
            ),
            RouteGroup(
                [
                    Get("/@account_id", "TransactionsController@show"),
                    Get("/roles", "TransactionsController@all_roles"),
                    Get("/permissions/@role", "TransactionsController@role_permissions")
                ],
                middleware=("auth",),
                prefix="/transactions",
            ),
        ],
        prefix="/api",
    ),
]
