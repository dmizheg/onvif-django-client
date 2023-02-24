from django.urls import path, re_path
from .views import(CameraView, CameraLoginView)
from .views import osd_changeName
from .views import my_view
from .views import my_ajax_view


urlpatterns = [

		re_path(r'^(?P<id>[^\.]+)/$', CameraView.as_view(), 
			name = "camera_detail"),
		re_path(r'^$', CameraLoginView.as_view(), 
			name = "camera_login"),
	    re_path(r'^(?P<id>\d+)$', osd_changeName, name='osd_changeName'),
        path('<int:param>', my_view, name='my_url'),
        re_path(r'^(?P<id>\d+)$', my_ajax_view, name='my_ajax_view'),


            
]

