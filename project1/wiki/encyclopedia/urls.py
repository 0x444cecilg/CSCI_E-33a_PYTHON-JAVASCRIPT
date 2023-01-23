from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<text>", views.page, name="entry_page"),
    path("search", views.search, name="search"),
    path("newentry", views.new, name="newentry"),
    path("edit/<text>", views.edit, name="edit"),
    path("random", views.randomm, name="random"),
]
