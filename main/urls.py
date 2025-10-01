from django.urls import path;

from . import views;

urlpatterns = [
    path("", views.index, name="index"),
    path("tag/create/", views.tagcreate, name="tagcreate"),
    path("artwork/upload/", views.upload, name="upload"),
    path("artwork/<int:pk>/", views.imageview, name="imageview"),
];

