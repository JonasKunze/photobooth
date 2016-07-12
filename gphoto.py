import re
import time

from PIL import Image
from PIL import ImageStat

import piggyphoto

class Wrapper(object):

    def __init__(self, subprocess):
        self._subprocess = subprocess

    def call(self, cmd):
        p = self._subprocess.Popen(cmd, shell=True, stdout=self._subprocess.PIPE,
            stderr=self._subprocess.PIPE, universal_newlines=True)
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
    """ A class which wraps calls to the external gphoto2 process. """

    def __init__(self, subprocess):
        Wrapper.__init__(self, subprocess)
        self._CMD = 'gphoto2'
        self.get_isos()
        self.piggy = piggyphoto.Camera()

    def capture_image_and_download(self):
        while self.piggy is None:
            print("waiting")
            time.sleep(1)
        filename = ".capture.jpg"
        self.piggy.capture_image(filename)
        return filename

    def set_shutter_speed(self, secs):
        print("Setting shutter_speed to %s"%secs)
        self.piggy.close()
        self.piggy = None
#        self.piggy.config.main.capturesettings.shutterspeed.value = secs
        while True:
            code, out, err = self.call([self._CMD + " --set-config /main/capturesettings/shutterspeed=" + str(secs)])
            if err != "":
                print(err)
            else:
                break
        self.piggy = piggyphoto.Camera()

    def get_isos(self):
        self._iso_choices = {100:0, 200:1, 400:2, 800:3, 1600:4} 

    def set_iso(self, iso):
        print("Setting iso to %d"%iso)
        #self.piggy.config.main.imgsettings.iso.value = self._iso_choices[iso] 
        self.piggy.close()
        self.piggy = None
        while True:
            code, out, err = self.call([self._CMD + " --set-config /main/imgsettings/iso=" + str(self._iso_choices[iso])])
            if err != "":
                print(err)
            else:
                break
        self.piggy = piggyphoto.Camera()


