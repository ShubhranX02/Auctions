from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("<int:id>/", views.display, name="display"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("add_to_watchlist/", views.add_to_watchlist, name="add_to_watchlist"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category>", views.view_category, name="view_category"),
    path("search/", views.search, name="search"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
]
