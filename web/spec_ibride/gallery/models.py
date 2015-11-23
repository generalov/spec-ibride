# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tagging.utils import calculate_cloud


class Photo(models.Model):
    """Модель Photo содержит данные о фотографии."""
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))
    user_id = models.IntegerField(verbose_name=_('user'))
    src = models.URLField(verbose_name=_('source'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created at'))
    rating = models.IntegerField(verbose_name=_('source'), default=0)
    tags = models.ManyToManyField('Tag', verbose_name=_('tags'))

    def update_tags(self, tag_names):
        current_tags = list(self.tags.all())

        # Remove tags which no longer apply
        tags_for_removal = [tag for tag in current_tags if tag.name not in tag_names]
        if len(tags_for_removal):
            self.tags.filter(tag__in=tags_for_removal).delete()

        # Add new tags
        current_tag_names = {tag.name for tag in current_tags}
        tag_names_to_add = (tag_name for tag_name in tag_names if tag_name not in current_tag_names)
        tags_to_add = (Tag.objects.get_or_create(name=tag_name) for tag_name in tag_names_to_add)
        self.tags.add(*[tag for tag, created in tags_to_add])

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        index_together = [
            ['created_at'],
            ['rating'],
        ]


class Tag(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    @classmethod
    def get_cloud(cls):
        qs = cls.objects.all().annotate(count=models.Count('name')).order_by('name')
        cloud = calculate_cloud(qs, steps=5)
        return cloud
