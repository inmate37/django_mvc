# Django
from django.urls import path

# Local
from .views import (
    CreateSongView,
    DeleteView,
    DetailView,
    FavoriteView,
    IndexView,
    create_album
)


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path(
        '<int:album_id>/',
        DetailView.as_view(),
        name='detail'
    ),
    path(
        '<int:album_id>/create_song/',
        CreateSongView.as_view(),
        name='create_song'
    ),
    path(
        '<int:song_id>/favorite/',
        FavoriteView.as_view(),
        name='favorite'
    ),
    path(
        '<int:album_id>/delete_song/<int:song_id>/',
        DeleteView.as_view(),
        name='delete_song'
    ),
    path(
        'create_album/',
        create_album,
        name='create_album'
    ),
]
