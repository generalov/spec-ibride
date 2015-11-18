# coding=utf-8
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Photo(models.Model):
    """Модель Photo содержит данные о фотографии."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))
    src = models.URLField(verbose_name=_('source'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    rating = models.IntegerField(verbose_name=_('source'), default=0)

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        index_together = [
            ['created_at'],
            ['rating'],
        ]
