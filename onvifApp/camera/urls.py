from django.conf.urls import url
from django.urls import path
from .views import(CameraView, CameraLoginView)
from .views import my_view


urlpatterns = [

		url(r'^(?P<id>[^\.]+)/$', CameraView.as_view(), 
			name = "camera_detail"),
		url(r'^$', CameraLoginView.as_view(), 
			name = "camera_login"),
        path('my_view/', my_view, 
            name='my_view'),

            
]

