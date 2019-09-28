"""Web Routes."""

from masonite.routes import Get, Post, Patch, RouteGroup

ROUTES = [
    Get("/", "WelcomeController@show").name("welcome"),
    Patch("/api/auth/seed_admin", "AuthController@seed_admin"),
]
