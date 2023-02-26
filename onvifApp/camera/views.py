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
from camera.config import PATHTOWSDL


# Create your views here.
class CameraView(View):



    def get(self, request, *args, **kwargs):
        
        # Get Hostname
        cam_obj = Camera.objects.get(id=kwargs['id'])
        mycam = None
        try:
            #mycam = ONVIFCamera(cam_obj.ip, cam_obj.port, cam_obj.username, cam_obj.password, PATHTOWSDL)
            mycam = MyCamera(cam_obj.ip,cam_obj.port, cam_obj.username, cam_obj.password)
            
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
        
        # Get network information

        config = mycam.get_network_config()

        param = {
                'hostname': hostname,
                'Manufacturer' : Manufacturer,'Model' : Model, 
                'FirmwareVersion': FirmwareVersion,
                'SerialNumber' : SerialNumber, 'HardwareId':HardwareId,
                'syslog_resp_list' : syslog_resp_list,
                'Sysdt_dt':Sysdt_dt, 'Sysdt_year' : Sysdt_year,
                'Sysdt_hour' : Sysdt_hour, 'Sysdt_tz' : Sysdt_tz,
                'NTP_server' : NTP_server, 'OSD_caption' : OSD_caption,
                'cam_id' : cam_obj.id, 'cam_ip' : cam_obj.ip, 'cam_pass' : cam_obj.password 
                }


        param = param | config

        #############
        return render(request, 'camera_detail.html', param)










def operation(request, id):
    op = request.GET.get('op')
    cam_ip = request.GET.get('cam_ip')
    cam_pass = request.GET.get('cam_pass')
  
    mycam = MyCamera(cam_ip,80, 'admin', cam_pass)

    if op == '1':
        osd_status = request.GET.get('osd_status')       
        caption = request.GET.get('caption')
        result = 'error'
        if osd_status == 'true':
            mycam.osd_enableName(caption)
            result = str(mycam.osd_changeName(caption))
            result = result+' Caption is Enabled. New name is: '+caption+' '+osd_status
        if osd_status == 'false':
            result = str(mycam.osd_delName())
            result = result+' Caption is Disabled'



        
    if op == '2':
        result = str(mycam.setNTP())

    if op == '5':
        new_dhcp = request.GET.get('new_dhcp')
        new_ip = request.GET.get('new_ip')
        new_mask = request.GET.get('new_mask')
        new_gateway = request.GET.get('new_gateway')
        result = mycam.set_network_config(False, new_ip, new_mask, new_gateway)
    
        
        #result = new_ip

  
    data = {
        
        'result': result
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
