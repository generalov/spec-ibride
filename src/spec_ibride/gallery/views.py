from django.shortcuts import render
from django.views.generic import ListView
from spec_ibride.gallery.models import Photo


class PhotoListView(ListView):
    model = Photo
    paginate_by = 20
    context_object_name = "photo_list"