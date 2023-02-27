from django.urls import path, re_path
from .views import(CameraView, CameraLoginView)
from .views import operation
from .views import ping_ip


urlpatterns = [

		re_path(r'^(?P<id>[^\.]+)/$', CameraView.as_view(), 
			name = "camera_detail"),
		re_path(r'^$', CameraLoginView.as_view(), 
			name = "camera_login"),
        re_path(r'^(?P<id>\d+)$', operation, name='operation'),
        path(' ', ping_ip, name='ping_ip'),

        


            
]

