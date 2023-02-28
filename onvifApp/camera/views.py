from django.shortcuts import render
from django.views.generic.base import View
from onvif import ONVIFCamera, exceptions
from django.shortcuts import redirect
from django.shortcuts import render
import os
from django.template import RequestContext
from onvifApp.settings import BASE_DIR
from camera.models import Camera
from onvif import ONVIFService
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
# import zeep
# from zeep.wsse.username import UsernameToken
from camera.camera import MyCamera
from camera.camera import CameraHost
from camera.config import PATHTOWSDL
import base64



# Create your views here.
class CameraView(View):

    def get(self, request, *args, **kwargs):
        
        # Get Hostname
        cam_obj = Camera.objects.get(id=kwargs['id'])
        mycam = None
        mycam1 = None
        try:
            
            mycam = MyCamera(cam_obj.ip,cam_obj.port, cam_obj.username, cam_obj.password)
            mycam1 = ONVIFCamera(cam_obj.ip, cam_obj.port, cam_obj.username, cam_obj.password, PATHTOWSDL)
           
        except Exception as e:
            print('Exception message : ' , str(e))
            cam_obj.delete()
            return render( request, 'camera_login.html', {'success': 'False'})

                    
        
        # Getdevice information

        try:
            resp = mycam.devicemgmt.GetHostname()
            hostname = str(resp.Name)
            resp = mycam.devicemgmt.GetDeviceInformation()
            Manufacturer = str(resp.Manufacturer)
            Model = str(resp.Model)
            FirmwareVersion = str(resp.FirmwareVersion)
            SerialNumber = str(resp.SerialNumber)
            HardwareId = str(resp.HardwareId)
        except Exception as e:
            print('Exception message : ' , str(e))
            cam_obj.delete()
            return render( request, 'camera_login.html', {'success': 'False'})

        ############
        # GetOSD information
        OSD_caption = mycam.osd_getName()



  
        #image_uri = 'http://admin:1beltelecombtk@10.252.45.232:85/images/snapshot.jpg'
        try:
            image_path = mycam.get_snapshot_uri(cam_obj.password)
            image_path = image_path.replace('http://','')
            #image_path = '10.252.45.232:85/images/snapshot.jpg'
            image_uri = f"http://{cam_obj.username}:{cam_obj.password}@{image_path}"
            pass
        except:
            print('errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrro')
            print('errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrro')
            image_uri = 'http://127.0.0.1:8000/static/blank.png'



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
            cam_obj.delete()
            return render( request, 'camera_login.html', {'success': 'False'})

        #############

        # Get date time 
        try:
            Sysdt_dt = mycam.devicemgmt.GetSystemDateAndTime()
            Sysdt_tz = Sysdt_dt.TimeZone
            Sysdt_year = Sysdt_dt.UTCDateTime.Date
            Sysdt_hour = Sysdt_dt.DaylightSavings
            NTP_server = mycam.devicemgmt.GetNTP().NTPManual[0].IPv4Address
        except Exception as e:
            print('Exception message : ' , str(e))
            cam_obj.delete()
            return render( request, 'camera_login.html', {'success': 'False'})
        
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
                'cam_id' : cam_obj.id, 'cam_ip' : cam_obj.ip, 'cam_pass' : cam_obj.password,
                'ImageURI' : image_uri
                }


        param = param | config

        #############
        return render(request, 'camera_detail.html', param)


                                  
          
                                   
          




def ping_ip(request):
    cam_ip = request.GET.get('cam_ip')
    host = CameraHost()
    result = host.ping_html_output(cam_ip)
    #result = str(proc).replace("\\n", "<br>")
    #result = str(result).replace("('", "")
    #result = str(result).replace("', None)", "")
    data = {        
        'result': result
    }
    return JsonResponse(data)



@csrf_exempt
def get_image(request, id):
    print('dfgsdfgsdfsdfsfsfsdfsdfsdsgds')
    if request.method == 'POST':
        mycam = MyCamera('192.168.0.12','80', 'admin', '1beltelecombtk')
        jpeg = mycam.get_snapshot('1beltelecombtk')  # получение изображения
        response = HttpResponse(jpeg, content_type='image/jpeg')
        response['Content-Disposition'] = 'attachment; filename=image.jpg'
        return response
    else:
        response_data = {'success': False, 'error': 'Метод не поддерживается'}
        return JsonResponse(response_data)
    

def operation(request, id):
    op = request.GET.get('op')
    cam_ip = request.GET.get('cam_ip')
    cam_pass = request.GET.get('cam_pass')
  
    mycam = MyCamera(cam_ip,80, 'admin', cam_pass)


 




    if op == 'reboot':
        result = str(mycam.reboot())

    if op == 'logout':
        result = 'ok'

    if op == '1':
        osd_status = request.GET.get('osd_status')       
        caption = request.GET.get('caption')
        result = 'error'
        if osd_status == 'true':
            mycam.osd_enableName(caption)
            result = str(mycam.osd_changeName(caption))
            result = 'Debug info: ' +result+' Caption is Enabled. New name is: '+caption+' '+osd_status
        if osd_status == 'false':
            result = str(mycam.osd_delName())
            result = 'Debug info: ' +result+' Caption is Disabled'


        
    if op == 'ntp':
        ntp_server_ip = request.GET.get('ntp_server_ip')
        result = str(mycam.setNTP(ntp_server_ip))
        result = 'Debug info: ' +result+' Set new NTP-server: ' + str(ntp_server_ip)

    if op == '5':
        new_dhcp = request.GET.get('new_dhcp')
        new_ip = request.GET.get('new_ip')
        new_mask = request.GET.get('new_mask')
        new_gateway = request.GET.get('new_gateway')
        new_dhcp = True if new_dhcp == 'true' else False

        result = mycam.set_network_config(new_dhcp, new_ip, new_mask, new_gateway)
        result = 'Debug info: Manual reboot: ' + str(result)



        

    data = {        
        'result': result
    }

    return JsonResponse(data)





def logout1(request, id):
    print("sdfsfsdsdfsfsdsdfsfsdsdfsfsdsdfsfsd")
    return HttpResponse("ok")

def logout(request, id):
    if request.method == 'POST':
        name = request.POST.get('name')
        return HttpResponse('Данные успешно отправлены!')
    else:
        return render(request, 'my_template.html')


 



class CameraLoginView(View):

    def get(self, request, *args, **kwargs):     
        return render( request, 'camera_login.html')

    def post(self, request, *args, **kwargs):
        ip = request.POST.get('ip-add','') 
        port = request.POST.get('port', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        obj = Camera.objects.create(ip=ip, port=port, username=username, password=password)
        print(obj.id)
        return redirect('camera_detail', obj.id)
