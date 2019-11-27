"""Web Routes."""

from masonite.routes import Get, Post, Patch, Put, RouteGroup

ROUTES = [
    Get("/", "WelcomeController@show").name("welcome"),
    RouteGroup(
        [
            Post("/auth/sign_in", "AuthController@sign_in"),
            RouteGroup(
                [
                    Get("/@user", "AccountController@user_by_id"),
                    Get("/gov_id/@user", "AccountController@user_by_gov_id"),
                    Post("/", "AccountController@register"),
                    Patch("/gov_id/@user", "AccountController@grant_edit_permissions"),
                    Put("/gov_id/@user", "AccountController@revoke_edit_permissions"),
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
                    Get(
                        "/permissions/@role", "TransactionsController@role_permissions"
                    ),
                ],
                middleware=("auth",),
                prefix="/transactions",
            ),
            RouteGroup(
                [Get("/@gov_id", "ConsentController@show")],
                prefix="/consent",
                middleware=("auth",),
            ),
        ],
        prefix="/api",
    ),
]
