import re
import time
import piggyphoto


from PIL import Image
from PIL import ImageStat

class Wrapper(object):

    def __init__(self, subprocess):
        self._subprocess = subprocess

    def call(self, cmd):
        p = self._subprocess.Popen(cmd, shell=True, stdout=self._subprocess.PIPE,
            stderr=self._subprocess.PIPE)
        out, err = p.communicate()
        return p.returncode, out.rstrip(), err.rstrip()

class ImageAnalyzer():

    @staticmethod
    def mean_brightness(filepath):
        im = Image.open(filepath)
        stat = ImageStat.Stat(im)
        rms = (stat.mean[0]+stat.mean[1]+stat.mean[2])/3
        im.close()
        return rms

class GPhoto(Wrapper):
    def __init__(self, subprocess):
        Wrapper.__init__(self, subprocess)
        self._CMD = 'gphoto2'
        self.get_shutter_speeds() 
        self.get_isos() 

        self.piggy = piggyphoto.camera()
        self.piggy.leave_locked()

    def capture_image_and_download(self):
        filename = "gphoto_capt.jpg"
        self.capture_image('image.jpg')
        return filename

    def get_shutter_speeds(self):
        code, out, err = self.call([self._CMD + " --get-config /main/capturesettings/shutterspeed"])
        if code != 0:
            raise Exception(err)
        choices = [] 
        current = None
        for line in out.split('\n'):
            if line.startswith('Choice:'):
                index = line.split(' ')[1]
                name = line.split(' ')[2]
                value = line.split(' ')[2]
                if "." not in value:
                    value = value+"."
                entry = {
                'value' : eval(value),
                'index' : index,
                'name' : name
                }
                choices.append(entry) 
            if line.startswith('Current:'):
                current = line.split(' ')[1]
        self._shutter_choices = choices
        return current, choices

    def set_shutter_speed(self, secs):
        self.piggy.config.main.capturesettings.shutterspeed.value = secs

    def get_isos(self):
        code, out, err = self.call([self._CMD + " --get-config /main/imgsettings/iso"])
        if code != 0:
            raise Exception(err)
        choices = {}
        current = None
        for line in out.split('\n'):
            if line.startswith('Choice:'):
                choices[line.split(' ')[2]] = int(line.split(' ')[1])
            if line.startswith('Current:'):
                current = line.split(' ')[1]
        self._iso_choices = choices
        return current, choices

    def set_iso(self, iso=None, index=None):
        if iso:
            self.piggy.config.main.imgsettings.iso.value = self._iso_choices[iso]
        if index:
            self.piggy.config.main.imgsettings.iso.value = index

