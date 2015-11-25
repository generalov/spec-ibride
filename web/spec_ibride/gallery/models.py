# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .utils import calculate_cloud
from .query import SizedRawQuerySet


class Photo(models.Model):
    """Фотография."""
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))
    user_id = models.IntegerField(verbose_name=_('user'))
    src = models.URLField(verbose_name=_('source'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    rating = models.IntegerField(verbose_name=_('source'), default=0)
    tags = models.ManyToManyField('Tag', verbose_name=_('tags'))

    @classmethod
    def find_by_tags(cls, included_tags=None, excluded_tags=None, using=None):
        """
        Ищет фотографии по пересечению тегов.

        В выборку попадают фотографии, которые содержат все теги из ``included_tags``, но при этом не содержат
        ни одного тега из ``excluded_tags``.

        :type included_tags: collections.Sized
        :type excluded_tags: collections.Sized
        :type using: None | str
        :param included_tags: набор тегов для включения фоторграфии в выборку (условие И).
        :param excluded_tags: набор тегов, исключающих фотографию из выборки (условие ИЛИ).
        :param using: альтернативный коннект к базе данных, если отличается.
        :return:
        """
        sql = str(cls.objects.all().query)
        query_parts = []
        query_params = []

        if included_tags:
            query_parts.append('''
               INNER JOIN (
                    SELECT p.id FROM gallery_photo p
                    INNER JOIN gallery_photo_tags pt ON p.id = pt.photo_id
                    INNER JOIN gallery_tag t ON pt.tag_id = t.id
                    WHERE t.name IN %s
                    GROUP BY p.id
                    HAVING count(*) = %s
                ) included on gallery_photo.id = included.id
            ''')
            query_params.extend([included_tags, len(included_tags)])

        if excluded_tags:
            query_parts.append('''
                LEFT JOIN (
                    SELECT DISTINCT pt.photo_id from gallery_photo_tags pt
                    INNER JOIN gallery_tag t ON pt.tag_id = t.id
                    WHERE t.name IN %s
                ) excluded ON gallery_photo.id = excluded.photo_id
                WHERE excluded.photo_id IS NULL
            ''')
            query_params.append(excluded_tags)

        raw_query = sql + ' '.join(query_parts)

        if using is None:
            using = cls.objects.db
        return SizedRawQuerySet(raw_query, model=cls.objects.model, params=query_params, using=using)

    def update_tags(self, tag_names):
        """
        Заменить теги.

        :type tag_names: collections.Sized
        :param tag_names: список новых тегов.
        :return:
        """
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
    """
    Тег.
    """
    name = models.CharField(verbose_name=_('name'), max_length=255, unique=True)
    cloud_steps = 5

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    @classmethod
    def get_cloud(cls, using=None):
        """
        Возвращает облако тегов.

        Добавляет атрибут ``weight`` каждому тегу в соответствии с частотой использования.
        Добавляет атрибут ``count`` каждому тегу в соответствии количеством использований.

        :param using:
        :return:
        """
        if using is None:
            using = cls.objects.db
        qs = SizedRawQuerySet('''
          SELECT `gallery_tag`.`id`, `gallery_tag`.`name`, COUNT('*') AS `count`
          FROM `gallery_tag`
          INNER JOIN `gallery_photo_tags` ON ( `gallery_tag`.`id` = `gallery_photo_tags`.`tag_id` )
          GROUP BY `gallery_tag`.`id`
          ORDER BY `gallery_tag`.`name` ASC''', model=cls.objects.model, using=using)
        cloud = calculate_cloud(qs, steps=cls.cloud_steps)
        return cloud
