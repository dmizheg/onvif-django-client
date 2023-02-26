########################################
# 24.02.2023
#
#
########################################
from onvif import ONVIFCamera, exceptions
from camera.config import PATHTOWSDL
import subprocess
from subprocess import check_output, STDOUT
from requests.auth import HTTPDigestAuth
import requests


class MyCamera(ONVIFCamera):
    def __init__(self, ip, port=80, user='admin', pswd='123'):
        try:
            super().__init__(ip, port, user, pswd, PATHTOWSDL)
            self.media_service = self.create_media_service()
            self.imaging_service = self.create_imaging_service()
            self.devicemgmt_service = self.create_devicemgmt_service()

            self.video_sources = self.media.GetVideoSources()
            self.source_configs = self.media_service.GetVideoSourceConfigurations()

            self.profiles = self.media.GetProfiles()

            self.VideoSourceConfigurationToken = self.source_configs[0].token
            self.OSDOptions = self.media_service.GetOSDs(self.VideoSourceConfigurationToken)

            self.network_interfaces = self.devicemgmt_service.GetNetworkInterfaces()
            self.ip_config = self.network_interfaces[0]
        except exceptions.ONVIFError as err:
            self.error = err
        else:
            self.error = False

    def reboot(self):  # Производит перезагрузку видеокамеры
        try:
            return self.devicemgmt.SystemReboot()
        except exceptions.ONVIFError as err:
            return "An error occurred while rebooting the device: %s" % err

    def assignName(self, newname):  # Назначает имя видеокамере
        try:
            self.devicemgmt.SetHostname(newname)
        except exceptions.ONVIFError as err:
            return "An error occurred while setting the device name: %s" % err

    def getName(self):  # Возвращает имя видеокамеры
        try:
            return self.devicemgmt.GetHostname().Name
        except exceptions.ONVIFError as err:
            return "An error occurred while getting the device name: %s" % err

    def getManufacturer(self):  # Возвращает произвводителя видеокамеры
        try:
            return self.devicemgmt.GetDeviceInformation().Manufacturer
        except exceptions.ONVIFError as err:
            return "An error occurred while getting the device manufacturer: %s" % err

    def getModel(self):  # Возвращает модель видеокамеры
        try:
            return self.devicemgmt.GetDeviceInformation().Model
        except exceptions.ONVIFError as err:
            return "An error occurred while getting the device model: %s" % err

    def getFirmwareVersion(self):  # Возвращает серийный прошивку видеокамеры
        try:
            return self.devicemgmt.GetDeviceInformation().FirmwareVersion
        except exceptions.ONVIFError as err:
            return "An error occurred while getting the firmware version: %s" % err

    def getSerialNumber(self):  # Возвращает серийный номер видеокамеры
        try:
            return self.devicemgmt.GetDeviceInformation().SerialNumber
        except exceptions.ONVIFError as err:
            return "An error occurred while getting the serial number: %s" % err

    def getHardwareId(self):  # Возвращает какой-то ИД видеокамеры
        try:
            return self.devicemgmt.GetDeviceInformation().HardwareId
        except exceptions.ONVIFError as err:
            return "An error occurred while getting the hardware id : %s" % err

    def getNTP(self):  # Возвращает настройки NTP
        if self.error:
            return self.error
        else:
            return self.devicemgmt.GetNTP().NTPManual[0].IPv4Address

    def setNTP(self):  # получаем информацию
        if self.error:
            return self.error
        else:
            dev_service = self.get_service("devicemgmt")
            param = {'FromDHCP': False, 'NTPManual': [{'Type': 'IPv4', 'IPv4Address': "10.1.0.1"}]}
            dev_service.SetNTP(param)
            return "OK"

    def setwdr(self, status):
        if self.error:
            return self.error
        else:
            imagingrequest = self.imaging_service.create_type('SetImagingSettings')
            imagingrequest.VideoSourceToken = self.video_sources[0].token
            if status == 'ON':
                param = {'WideDynamicRange': {'Mode': "ON", 'Level': 50}}
            else:
                param = {'WideDynamicRange': {'Mode': "OFF"}}
            imagingrequest.ImagingSettings = param
            self.imaging_service.SetImagingSettings(imagingrequest)
            return 'OK'

    def get_snapshot(self, password):
        try:
            # profiles = self.media_service.GetProfiles()
            for profile in self.profiles:
                snapshot = self.media_service.create_type('GetSnapshotUri')
            snapshot.ProfileToken = profile.token
            output_snap_uri = self.media_service.GetSnapshotUri(snapshot)
            data = requests.get(str(output_snap_uri.Uri), auth=HTTPDigestAuth('admin', password), verify=False,
                                stream=True).content
            result = data
        except exceptions.ONVIFError as err:
            result = ("An error occurred while getting snapshot: %s" % err)
        return result

    def osd_getName(self):
        if self.error:
            return self.error
        else:
            try:
                return self.OSDOptions[1].TextString.PlainText
            except:
                return "OSD caption is disabled"

    def osd_changeName(self, caption):
        if self.error:
            return self.error
        else:
            try:
                self.OSDOptions[1].TextString.PlainText = caption
                self.media_service.SetOSD(self.OSDOptions[1])
            except:
                return "OSD caption is disabled"
            else:
                return "OK"

    def osd_delName(self):
        if self.error:
            return self.error
        else:
            try:
                osd_channel_token1 = self.media.GetOSDs(self.VideoSourceConfigurationToken)[1].token  # 'Type': 'Plain'
                self.media.DeleteOSD(osd_channel_token1)
            except:
                return "OSD caption already is disabled"
            else:
                return "OK"

    def osd_enableName(self, caption):

        def create_config(caption):
            osd = self.media.create_type('CreateOSD')
            osd.OSD = {
                'token': 'token0',
                'Position': {
                    'Type': 'Custom',
                    'Pos': {
                        'x': 0.45,
                        'y': -0.80
                    },
                },
                'TextString': {
                    'PlainText': f'{caption}',
                    'Type': 'Plain',
                },
                'Type': 'Text',
                'VideoSourceConfigurationToken': self.profiles[0].VideoSourceConfiguration.token,
            }
            self.media.CreateOSD(osd)

        if self.error:
            return self.error
        else:
            try:
                old_caption = self.OSDOptions[1].TextString.PlainText
            except:
                create_config(caption)
                return "OK"
            # если надпись есть, но не включена - включаем, но оставляем старую надпись
            osd_channel_token1 = self.media.GetOSDs(self.VideoSourceConfigurationToken)[1].token  # 'Type': 'Plain'
            self.media.DeleteOSD(osd_channel_token1)
            create_config(old_caption)
            return "Enabled, but OSD caption already had text"

    def get_network_config(self):
        if self.error:
            return self.error
        else:
            gateway_config = self.devicemgmt_service.GetNetworkDefaultGateway()
            gateway = gateway_config.IPv4Address[0]
            dhcp_enable_flag = self.ip_config.IPv4.Config.DHCP
            if dhcp_enable_flag:
                config = {
                   'DHCP': self.ip_config.IPv4.Config.DHCP
                   }
            else:
                config = {
                   'DHCP': self.ip_config.IPv4.Config.DHCP,
                   'IPv4': self.ip_config.IPv4.Config.Manual[0].Address,
                   'PrefixLength': self.ip_config.IPv4.Config.Manual[0].PrefixLength,
                   'Gateway': gateway
                   }
            return config



class CameraHost():
    def ping(self, host):  # ping
        try:
            # result = subprocess.Popen(['ping', '-c 3', '-i 2', f'{host}'], stdout=subprocess.PIPE, encoding='cp866').communicate()
            result = check_output(['ping -c 3 -i 2 ' + host], stderr=STDOUT, shell=True, encoding='cp866')
        except subprocess.CalledProcessError as err:
            result = ("An error occurred while trying ping: %s" % err.output)
        return result
