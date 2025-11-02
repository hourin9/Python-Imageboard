from django.urls import path;

from . import views;

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_page, name="login"),
    path("logout", views.logout_page, name="logout"),
    path("register", views.register_page, name="register"),
    path("tag/create/", views.tagcreate, name="tagcreate"),
    path("tag/<str:pk>/delete/", views.tag_delete, name="tagdelete"),

    path("artwork/<int:pk>/upvote", views.artwork_upvote, name="upvote"),
    path("artwork/<int:pk>/downvote", views.artwork_downvote, name="downvote"),
    path("artwork/upload/", views.artwork_upload, name="upload"),
    path("artwork/<int:pk>/", views.imageview, name="imageview"),
    path("artwork/<int:pk>/delete/", views.artwork_delete, name="imagedelete"),
    path("artwork/<int:pk>/edit/", views.artwork_update, name="imageupdate"),
];

