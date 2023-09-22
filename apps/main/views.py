# Python
from typing import Any

# Django
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.http.response import (
    HttpResponse,
    JsonResponse
)
from django.shortcuts import render
from django.views import View

# First party
from abstracts.utils import get_object_or_404

# Local
from .forms import (
    AlbumForm,
    SongForm
)
from .models import (
    Album,
    AudioFileType,
    Song
)


class IndexView(View):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, QuerySet[Any]]:
        albums: QuerySet[Album] = Album.objects.not_deleted()
        context: dict[str, QuerySet[Any]] = {
            'albums': albums
        }
        return context

    def get(
        self,
        request: WSGIRequest,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponse:

        context: dict[str, QuerySet[Any]] = self.get_context_data()
        return render(
            request,
            self.template_name,
            context
        )


class DetailView(View):
    template_name = 'main/detail.html'

    def get_context_data(
        self,
        album_id: int,
        **kwargs: dict
    ) -> dict[str, QuerySet[Any]]:

        album: Album = get_object_or_404(Album, album_id)
        user: User = self.request.user
        context: dict[str, Any] = {
            'album': album,
            'user': user
        }
        return context

    def get(
        self,
        request: WSGIRequest,
        album_id: int,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponse:

        context: dict[str, QuerySet[Any]] = \
            self.get_context_data(album_id)

        return render(
            request,
            self.template_name,
            context
        )


class DeleteView(View):
    template_name = 'main/detail.html'

    def get_context_data(
        self,
        album_id: int,
        **kwargs: Any
    ) -> dict[str, QuerySet[Any]]:

        album: Album = get_object_or_404(Album, album_id)
        context: dict[str, QuerySet[Any]] = {'album': album}
        return context

    def post(
        self,
        request: WSGIRequest,
        album_id: int,
        song_id: int,
        *args: Any,
        **kwargs: Any
    ) -> HttpResponse:

        context: dict[str, QuerySet[Any]] = \
            self.get_context_data(album_id)

        song: Song = context['album'].songs.get(id=song_id)
        song.delete()

        return render(
            request,
            self.template_name,
            context
        )


class CreateSongView(View):
    """
    Вьюшка для создания песен.
    """
    template_name = 'main/create_song.html'

    def get(
        self,
        request: WSGIRequest,
        album_id: int
    ) -> HttpResponse:

        album: Album = get_object_or_404(Album, album_id)
        form: SongForm = SongForm()
        context: dict[str, Any] = {
            'album': album,
            'form': form
        }
        return render(
            request,
            self.template_name,
            context
        )

    def post(
        self,
        request: WSGIRequest,
        album_id: int
    ) -> HttpResponse:

        album: Album = get_object_or_404(Album, album_id)
        form: SongForm = SongForm(
            request.POST or None,
            request.FILES or None
        )
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    'album': album,
                    'form': form
                }
            )
        album_songs: QuerySet[str] = \
            album.songs.values_list('title', flat=True)

        if form.cleaned_data.get('title') in album_songs:
            return render(
                request,
                self.template_name,
                {
                    'album': album,
                    'form': form,
                    'error_message': 'Вы уже добавляли эту песню'
                }
            )

        song: SongForm = form.save(commit=False)
        song.album = album
        song.audio_file = request.FILES['audio_file']

        file_type: str = song.audio_file.url.split('.')[-1]
        file_type = file_type.lower()

        audio_file_types: QuerySet[str] = \
            AudioFileType.objects.values_list('name', flat=True)

        if file_type not in audio_file_types:
            return render(
                request,
                self.template_name,
                {
                    'album': album,
                    'form': form,
                    'error_message': 'Неверный формат аудио-файла'
                }
            )
        song.save()
        return render(
            request,
            'main/detail.html',
            {'album': album}
        )


class FavoriteView(View):
    """
    FavoriteView.
    """
    def get(self, request: WSGIRequest, song_id: int) -> JsonResponse:
        song = get_object_or_404(
            Song,
            song_id
        )
        try:
            song.is_favorite = not song.is_favorite
            song.save(
                update_fields=('is_favorite',)
            )
        except (
            KeyError,
            Song.DoesNotExist
        ):
            return JsonResponse({'success': False})

        return JsonResponse({'success': True})



def create_album(request):
    IMAGE_FILE_TYPES = (
        'png',
        'jpg',
        'jpeg'
    )
    form = AlbumForm(
        request.POST or None,
        request.FILES or None
    )
    if not form.is_valid():
        return render(
            request,
            'main/create_album.html',
            {'form': form}
        )
    album = form.save(commit=False)
    album.logo = request.FILES['logo']
    file_type = album.file_type
    file_type = file_type.lower()

    if file_type not in IMAGE_FILE_TYPES:
        return render(
            request,
            'main/create_album.html',
            {
                'album': album,
                'form': form,
                'error_message': 'Image file must be PNG, JPG, or JPEG',
            }
        )
    album.save()
    return render(
        request,
        'main/detail.html',
        {'album': album}
    )
