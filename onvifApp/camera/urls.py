from django.urls import path, re_path
from .views import(CameraView, CameraLoginView)
from .views import operation
from .views import ping_ip
from .views import logout
from .views import get_image




urlpatterns = [

		re_path(r'^(?P<id>[^\.]+)/$', CameraView.as_view(), name = "camera_detail"),
		re_path(r'^$', CameraLoginView.as_view(), name = "camera_login"),
        path('<int:id>/', get_image, name='get_image'),
        path('<int:id>/', logout, name='logout'),
        re_path(r'^(?P<id>\d+)$', operation, name='operation'),
        path(' ', ping_ip, name='ping_ip'),



        


            
]

