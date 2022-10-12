from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("categories", views.categories, name="categories"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("createListing", views.createListing, name="createListing"),
    path("listings/<int:listing_id>", views.listing, name="listings"),
    path("closeListing/<int:listing_id>", views.closeListing, name="closeListing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]