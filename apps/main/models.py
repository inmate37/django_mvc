# Python
from typing import Any

# Django
from django.contrib.auth.models import User
from django.db import models

# First party
from abstracts.models import AbsctractDateTime
from abstracts.utils import normalize_time


class AudioFileType(models.Model):
    """
    Модель для хранения типов расширений аудио-файлов.
    """
    name: models.CharField = models.CharField(
        verbose_name='название',
        max_length=10
    )

    class Meta:
        verbose_name = 'тип расширения аудио-файла'
        verbose_name_plural = 'типы расширений аудио-файлов'

    def __str__(self):
        return f'Расширение: {self.name}'


class Country(models.Model):
    title = models.CharField(
        verbose_name='название',
        max_length=50
    )

    class Meta:
        verbose_name = 'страна'
        verbose_name_plural = 'страны'

    def __str__(self):
        return self.title


class Band(AbsctractDateTime):
    title = models.CharField(
        verbose_name='название',
        max_length=50
    )
    followers = models.PositiveIntegerField(
        verbose_name='фоловеры',
        default=0
    )
    country = models.ForeignKey(
        to=Country,
        on_delete=models.PROTECT,
        verbose_name='страна'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self) -> str:
        if not self.title:
            return 'Без названия'
        return f'Группа: {self.title}'


class Artist(AbsctractDateTime):
    """
    Artist model.
    """
    GENDER_OTHER = 0
    GENDER_FEMALE = 1
    GENDER_MALE = 2
    GENDERS = (
        (GENDER_OTHER, 'Остальное'),
        (GENDER_FEMALE, 'Женщина'),
        (GENDER_MALE, 'Мужчина')
    )
    band = models.ForeignKey(
        to=Band,
        on_delete=models.PROTECT,
        verbose_name='группа',
        null=True,
        blank=True
    )
    user = models.OneToOneField(
        to=User,
        on_delete=models.PROTECT,
        verbose_name='пользователь',
        null=True,
        blank=True
    )
    nickname = models.CharField(
        verbose_name='псевдоним',
        default='',
        max_length=50
    )
    gender = models.PositiveSmallIntegerField(
        choices=GENDERS,
        verbose_name='гендер',
        default=GENDER_OTHER
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'музыкант'
        verbose_name_plural = 'музыканты'

    def __str__(self) -> str:
        if not self.nickname:
            return 'Без имени'

        return f'Музыкант: {self.nickname}'


class AlbumQuerySet(models.QuerySet):

    def not_deleted(self):
        return self.filter(is_deleted=False)


class AlbumManager(models.Manager):

    def get_queryset(self) -> models.query.QuerySet['Album']:
        return AlbumQuerySet(
            self.model,
            using=self._db
        )

    def not_deleted(self):
        return self.get_queryset().not_deleted()


class Album(models.Model):
    """
    Album model.
    """
    REGULAR = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3
    STATUSES = (
        (REGULAR, 'Обычный'),
        (SILVER, 'Серебряный'),
        (GOLD, 'Золотой'),
        (PLATINUM, 'Платиновый'),
    )
    band = models.ForeignKey(
        to=Band,
        on_delete=models.PROTECT,
        verbose_name='группа'
    )
    title = models.CharField(
        verbose_name='название альбома',
        max_length=150
    )
    release_date = models.DateTimeField(
        verbose_name='дата релиза',
    )
    logo = models.ImageField(
        verbose_name='логотип',
        upload_to='album_covers/%Y/',
        default='media/default_cover.png',
        null=True,
        blank=True
    )
    status = models.SmallIntegerField(
        choices=STATUSES,
        default=REGULAR,
        verbose_name='статус'
    )
    is_deleted = models.BooleanField(
        verbose_name='удален',
        default=False
    )
    objects = AlbumManager()

    def __str__(self) -> str:
        return f'{self.band}: {self.title} ({self.status})'

    @property
    def file_type(self):
        LAST: int = -1
        return self.logo.url.split('.')[LAST]

    class Meta:
        ordering = ('release_date',)
        verbose_name = 'альбом'
        verbose_name_plural = 'альбомы'


class Genre(models.Model):
    """Genre model."""

    title = models.CharField(
        max_length=50,
        verbose_name='жанр'
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'
        ordering = ('-id',)


class Song(models.Model):
    """Song model."""

    title = models.CharField(
        verbose_name='название песни',
        max_length=50
    )
    album = models.ForeignKey(
        to=Album,
        on_delete=models.CASCADE,
        verbose_name='альбом',
        related_name='songs'
    )
    audio_file = models.FileField(
        verbose_name='аудио файл',
        upload_to='songs/%Y/%m/%d/'
    )
    duration = models.PositiveSmallIntegerField(
        verbose_name='длительность трека',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        to=Genre,
        verbose_name='жанр'
    )
    # TODO: отправлять email при достижении
    #       100 прослушиваний
    #       1000 прослушиваний итд.
    #
    times_played = models.PositiveIntegerField(
        verbose_name='количество прослушиваний',
        null=True,
        blank=True
    )
    is_favorite = models.BooleanField(
        verbose_name='избранное',
        default=False
    )

    @property
    def normalized_duration(self) -> str:
        return normalize_time(
            self.duration
        )

    def __str__(self) -> str:
        return f'Song: {self.title}'

    def save(self, *args: Any, **kwargs: Any) -> None:
        # TODO: сделать валидацию на аудио-файл
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'песня'
        verbose_name_plural = 'песни'
        ordering = ('id',)
