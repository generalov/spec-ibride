# coding=utf-8
from django.http.response import Http404
from django.views.generic import ListView
from django.utils.translation import ugettext_lazy as _

from spec_ibride.gallery.models import Photo
from tagging.models import TaggedItem
from tagging.utils import calculate_cloud


class PhotoListView(ListView):
    """
    :attribute request: django.http.request.HttpRequest
    """
    model = Photo
    paginate_by = 20
    context_object_name = "photo_list"
    all_ordering = [
        {'title': _('popular'), 'name': 'popular', 'order_by': ['-rating']},
        {'title': _('recent'), 'name': 'recent', 'order_by': ['-created_at']},
    ]
    default_ordering = 'recent'
    ordering_kwarg = 'ordering'
    max_selected_tags = 5
    tag_kwarg = 'tag'

    def get_context_data(self, **kwargs):
        data = super(PhotoListView, self).get_context_data(**kwargs)
        tag_cloud = self._get_tagcloud_data()
        data['tag_cloud'] = tag_cloud
        data['getvars'] = [self.ordering_kwarg, self.tag_kwarg]  # for
        data['ordering_list'] = self._get_ordering_data()
        return data

    def get_ordering(self):
        """Вернуть порядок сортировки"""
        ordering = self._get_requested_ordering()
        by_name = dict((x['name'], x) for x in self.all_ordering)
        if ordering not in by_name:
            raise Http404()
        return by_name[ordering]['order_by']

    def get_queryset(self):
        qs = super(PhotoListView, self).get_queryset()
        requested_tags = self._get_requested_tags()
        if requested_tags:
            qs = TaggedItem.objects.get_union_by_model(qs, requested_tags)
        return qs

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
        """Вернуть данные для облака тегов"""
        tag_cloud = calculate_cloud(Photo.tags.usage(counts=True), steps=5)
        requested_tags = self._get_requested_tags()
        is_tag_limit_reached = len(requested_tags) >= self.max_selected_tags
        for tag in tag_cloud:
            query = self.request.GET.copy()
            if self.page_kwarg in query:
                del query[self.page_kwarg]
            is_active = tag.name in requested_tags
            if is_active:
                query.getlist(self.tag_kwarg, []).remove(tag.name)
            elif not is_tag_limit_reached:
                query.appendlist(self.tag_kwarg, tag.name)
            is_disabled = is_tag_limit_reached and not is_active
            url = self.request.path + '?' + query.urlencode()
            tag.active = is_active
            tag.disabled = is_disabled
            tag.url = url
        return tag_cloud

    def _get_requested_ordering(self):
        return self.request.GET.get(self.ordering_kwarg, self.default_ordering)

    def _get_requested_tags(self):
        """Вернуть список тегов из запроса если есть"""
        return self.request.GET.getlist(self.tag_kwarg, [])[:self.max_selected_tags]
