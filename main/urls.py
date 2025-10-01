from django.urls import path;

from . import views;

urlpatterns = [
    path("", views.index, name="index"),
    path("tag/create/", views.tagcreate, name="tagcreate"),
    path("tag/<str:pk>/delete/", views.tag_delete, name="tagdelete"),

    path("artwork/upload/", views.upload, name="upload"),
    path("artwork/<int:pk>/", views.imageview, name="imageview"),
    path("artwork/<int:pk>/delete/", views.artwork_delete, name="imagedelete"),
];

