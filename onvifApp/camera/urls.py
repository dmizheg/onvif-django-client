from django.urls import path, re_path
from .views import(CameraView, CameraLoginView)
from .views import osd_changeName
from .views import ntp_enable
from .views import operation


urlpatterns = [

		re_path(r'^(?P<id>[^\.]+)/$', CameraView.as_view(), 
			name = "camera_detail"),
		re_path(r'^$', CameraLoginView.as_view(), 
			name = "camera_login"),
        re_path(r'^(?P<id>\d+)$', operation, name='operation'),
       # re_path(r'^(?P<id>\d+)$', ntp_enable, name='ntp_enable'),
        #re_path(r'^(?P<id>\d+)$', osd_changeName, name='osd_changeName'),
        


            
]

