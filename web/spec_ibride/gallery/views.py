# coding=utf-8
import six
from django.http.response import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from spec_ibride.gallery.models import Photo, Tag


class PhotoListView(ListView):
    """
    :attribute request: django.http.request.HttpRequest
    """
    model = Photo
    paginate_by = 20
    context_object_name = 'photo_list'
    all_ordering = [
        {'title': _('popular'), 'name': 'popular', 'order_by': ['-rating']},
        {'title': _('recent'), 'name': 'recent', 'order_by': ['-created_at']},
    ]
    default_ordering = 'recent'
    ordering_kwarg = 'ordering'
    max_tags = 5
    max_x_tags = 3
    tag_kwarg = 'tag'
    x_tag_kwarg = 'xtag'

    def get_context_data(self, **kwargs):
        data = super(PhotoListView, self).get_context_data(**kwargs)
        tag_cloud = self._get_tagcloud_data()
        data['tag_cloud'] = tag_cloud
        data['getvars'] = [self.ordering_kwarg, self.tag_kwarg]  # for
        data['ordering_list'] = self._get_ordering_data()
        return data

    def get_ordering(self):
        """Вернуть порядок сортировки."""
        ordering = self._get_requested_ordering()
        by_name = dict((x['name'], x) for x in self.all_ordering)
        if ordering not in by_name:
            raise Http404()
        return by_name[ordering]['order_by']

    def get_queryset(self):
        requested_tags = self._get_requested_tags()
        requested_x_tags = self._get_requested_x_tags()
        if requested_tags or requested_x_tags:
            queryset = Photo.find_by_tags(included_tags=requested_tags, excluded_tags=requested_x_tags)
            ordering = self.get_ordering()
            if ordering:
                if isinstance(ordering, six.string_types):
                    ordering = (ordering,)
                queryset = queryset.order_by(*ordering)
        else:
            queryset = super(PhotoListView, self).get_queryset()
        return queryset

    def _get_ordering_data(self):
        res = []
        for ordering in self.all_ordering:
            is_active = self._get_requested_ordering() == ordering['name']
            query = self.request.GET.copy()
            query[self.ordering_kwarg] = ordering['name']
            o = {
                'title': ordering['title'],
                'active': is_active,
                'url': self.request.path + '?' + query.urlencode()
            }
            res.append(o)
        return res

    def _get_tagcloud_data(self):
        """
        Вернуть данные для облака тегов.

        normal -> included -> excluded -> normal
        """
        tag_cloud = Tag.get_cloud()
        requested_tags = self._get_requested_tags()
        requested_x_tags = self._get_requested_x_tags()
        is_tag_limit_reached = len(requested_tags) >= self.max_tags
        is_x_tag_limit_reached = len(requested_x_tags) >= self.max_x_tags
        for tag in tag_cloud:
            query = self.request.GET.copy()
            if self.page_kwarg in query:
                del query[self.page_kwarg]
            is_included = tag.name in requested_tags
            is_excluded = tag.name in requested_x_tags
            if is_included:
                query.getlist(self.tag_kwarg, []).remove(tag.name)
                if not is_x_tag_limit_reached:
                    query.appendlist(self.x_tag_kwarg, tag.name)
            elif is_excluded:
                query.getlist(self.x_tag_kwarg, []).remove(tag.name)
            elif not is_tag_limit_reached:
                query.appendlist(self.tag_kwarg, tag.name)
            is_disabled = is_tag_limit_reached and not is_included
            url = self.request.path + '?' + query.urlencode()
            tag.active = is_included
            tag.excluded = is_excluded
            tag.disabled = is_disabled
            tag.url = url
        return tag_cloud

    def _get_requested_ordering(self):
        return self.request.GET.get(self.ordering_kwarg, self.default_ordering)

    def _get_requested_tags(self):
        """Вернуть список тегов из запроса если есть."""
        return self.request.GET.getlist(self.tag_kwarg, [])[:self.max_tags]

    def _get_requested_x_tags(self):
        """Вернуть список исключающих тегов из запроса если есть."""
        return self.request.GET.getlist(self.x_tag_kwarg, [])[:self.max_x_tags]
