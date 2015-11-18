from django.http.response import Http404
from django.views.generic import ListView
from spec_ibride.gallery.models import Photo


class PhotoListView(ListView):
    model = Photo
    paginate_by = 20
    context_object_name = "photo_list"
    valid_orders = {
        'popular': ['-rating'],
        'recent': ['-created_at'],
    }

    def get_ordering(self):
        ordering = self.request.GET.get('ordering', 'recent')
        if ordering not in self.valid_orders:
            raise Http404()
        return self.valid_orders[ordering]

    def get_context_data(self, **kwargs):
        data = super(PhotoListView, self).get_context_data(**kwargs)
        data['getvars'] = ['ordering']
        return data
