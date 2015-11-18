from django.conf.urls import url

from .views import PhotoListView

urlpatterns = [
    url(r'^$', PhotoListView.as_view(), name='photo-list'),
]