from django.shortcuts import render
from django.views.generic.base import View
from onvif import ONVIFCamera
from django.shortcuts import redirect
from django.shortcuts import render
import os
from django.template import RequestContext
from onvifApp.settings import BASE_DIR
from camera.models import Camera
from onvif import ONVIFService
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# import zeep
# from zeep.wsse.username import UsernameToken
from camera.camera import MyCamera


# Create your views here.
class CameraView(View):



    def get(self, request, *args, **kwargs):
        
        # Get Hostname
        cam_obj = Camera.objects.get(id=kwargs['id'])
        mycam = None
        try:
            #mycam = ONVIFCamera(cam_obj.ip, cam_obj.port, cam_obj.username, cam_obj.password, '/Users/zhegulovichds/PycharmProjects/pythonProject/venv/lib/python3.9/site-packages/wsdl/')
            mycam = ONVIFCamera(cam_obj.ip, cam_obj.port, cam_obj.username, cam_obj.password, '/home/zhegulovichds/.local/lib/python3.10/site-packages/wsdl')
            
        except Exception as e:
            print('Exception message : ' , str(e))
            cam_obj.delete()
            return render( request,
			        'camera_login.html', {'success': 'False'})
        
        # Getdevice information

        resp = mycam.devicemgmt.GetHostname()
        hostname = str(resp.Name)
        resp = mycam.devicemgmt.GetDeviceInformation()
        Manufacturer = str(resp.Manufacturer)
        Model = str(resp.Model)
        FirmwareVersion = str(resp.FirmwareVersion)
        SerialNumber = str(resp.SerialNumber)
        HardwareId = str(resp.HardwareId)

        ############
        # GetOSD information
        OSD_caption = " "
        try:
            media_service = mycam.create_media_service()
            source_configs = media_service.GetVideoSourceConfigurations()
            VideoSourceConfigurationToken = source_configs[0].token
            OSDOptions = media_service.GetOSDs(VideoSourceConfigurationToken)
            OSD_caption = OSDOptions[1].TextString.PlainText
        except Exception as e:
            print('Exception message : ' , str(e))


  


        ############

        # Get System log

        syslog_obj = mycam.devicemgmt.create_type('GetSystemLog')
        #print('#######' , syslog_obj)
        syslog_obj['LogType'] = 'Access'
        syslog_resp_list = None
        try:
            syslog_resp = mycam.devicemgmt.GetSystemLog({'LogType' : syslog_obj.LogType})
            syslog_resp_list = str(syslog_resp.String).split('\n')
            #print(syslog_resp_list)
        except Exception as e:
            print('System log error: ', str(e))

        #############

        # Get date time 

        Sysdt_dt = mycam.devicemgmt.GetSystemDateAndTime()
        Sysdt_tz = Sysdt_dt.TimeZone
        Sysdt_year = Sysdt_dt.UTCDateTime.Date
        Sysdt_hour = Sysdt_dt.DaylightSavings
        NTP_server = mycam.devicemgmt.GetNTP().NTPManual[0].IPv4Address
        
        #############


        return render( request,
			'camera_detail.html', {'hostname': hostname,
                'Manufacturer' : Manufacturer,'Model' : Model, 
                'FirmwareVersion': FirmwareVersion,
                'SerialNumber' : SerialNumber, 'HardwareId':HardwareId,
                'syslog_resp_list' : syslog_resp_list,
                'Sysdt_dt':Sysdt_dt, 'Sysdt_year' : Sysdt_year,
                'Sysdt_hour' : Sysdt_hour, 'Sysdt_tz' : Sysdt_tz,
                'NTP_server' : NTP_server, 'OSD_caption' : OSD_caption,
                'cam_id' : cam_obj.id, 'cam_ip' : cam_obj.ip, 'cam_pass' : cam_obj.password
                 })










def operation(request, id):
    op = request.GET.get('op')
    caption = request.GET.get('caption')
    cam_ip = request.GET.get('cam_ip')
    cam_pass = request.GET.get('cam_pass')
  
    mycam = MyCamera(cam_ip,80, 'admin', cam_pass)

    if op == '1':
        result = str(mycam.osd_changeName(caption))
    if op == '2':
        result = str(mycam.setNTP())
    if op == '3':
        result = str(mycam.osd_delName())
    if op == '4':
        result = str(mycam.osd_enableName(caption))
        
        

  
    data = {
        
        'test': result
    }
    return JsonResponse(data)














def osd_changeName(request, id):
    caption = request.GET.get('caption')
    cam_ip = request.GET.get('cam_ip')
    cam_pass = request.GET.get('cam_pass')
  
    mycam = MyCamera(cam_ip,80, 'admin', cam_pass)
    result = str(mycam.osd_changeName(caption))

  
    data = {
        
        'test': result
    }
    return JsonResponse(data)





def ntp_enable(request, id):
    cam_ip = request.GET.get('cam_ip')
    cam_pass = request.GET.get('cam_pass')

    mycam = MyCamera(cam_ip,80, 'admin', cam_pass)
    result = str(mycam.setNTP())
   
    
    data = {
        'test': result
    }
    return JsonResponse(data)
















def get_objects(request):
 
    return JsonResponse({'message': 'Функция выполнена успешно.'})


def is_even(request, number):
    number = int(request.GET.get('number'))
    result = number % 2 == 0
    data = {

        'is_even': result
    }
    return JsonResponse(data)





class CameraLoginView(View):

    def get(self, request, *args, **kwargs):     
        return render( request,
			'camera_login.html')

    def post(self, request, *args, **kwargs):
        ip = request.POST.get('ip-add','') 
        port = request.POST.get('port', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        obj = Camera.objects.create(ip=ip, port=port,
            username=username, password=password)
        print(obj.id)
        return redirect(
			'camera_detail', obj.id)
