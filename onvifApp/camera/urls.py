from django.urls import path
from django.urls import re_path
from .views import(CameraView, CameraLoginView)
from .views import my_view
from .views import get_objects
from .views import is_even


urlpatterns = [

		re_path(r'^(?P<id>[^\.]+)/$', CameraView.as_view(), name = "camera_detail"),
		re_path(r'^$', CameraLoginView.as_view(), name = "camera_login"),
        re_path(r'^sd\d', my_view, name='my_view'),
        re_path(r'^dd\d+', get_objects, name='get-objects'),
        re_path(r'^(?P<nnn>)/' , is_even, name='is-even'),

            
]

