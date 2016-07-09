# coding: utf-8

from gphoto import GPhoto
from gphoto import ImageAnalyzer 
import RPi.GPIO as GPIO
from gpio import *
import subprocess
import math
import os
import time
import traceback
from subprocess import call

BRIGHTNESS = 112 

CONFIGS = [("1/1600", 100),
        ("1/1000", 100),
        ("1/800", 100),
        ("1/500", 100),
        ("1/320", 100),
        ("1/250", 100),
        ("1/200", 100),
        ("1/160", 100),
        ("1/100", 100),
        ("1/80", 100),
        ("1/60", 100),
        ("1/50", 100),
        ("1/80", 200),
        ("1/60", 200),
        ("1/50", 200),
        ("1/40", 200),
        ("1/40", 200),
        ("1/25", 200),
        ("1/20", 200),
        ("1/15", 200),
        ("1/25", 400),
        ("1/20", 400),
        ("1/15", 400),
        ("1/13", 400),
        ("1/10", 400),
        ("1/15", 800),
        ("1/13", 800),
        ("1/10", 800),
        ("1/15", 1600),
        ("1/13", 1600),
        ("1/10", 1600),
        ]


class Cam():
    def __init__(self):
        self.config_file = ".cam-configs" 
        self.filename = None
        self.config = len(CONFIGS)/2 
        try:
            with open(self.config_file, 'r') as f:
                self.config = int(f.readline())
                print("Found cam config file: %d"%self.config)
        except IOError:
            self.config = len(CONFIGS)/2
            print("No cam config file found. Using default: %d"%self.config)

        self.pic_id = 0
        self.camera = GPhoto(subprocess)
        while True:
            try:
                self.change_setting(0)
                break
            except Exception as e:  
                call(["pkill", "gvfs-gphoto2*"])
                call(["killall", "-9", "gvfsd-gphoto2"])
                print("Exception caught: {0}".format(e))
                traceback.print_exc(e)

    def change_setting(self, delta):
        self.config = self.config + delta
        self.camera.set_shutter_speed(secs=CONFIGS[self.config][0])

        self.camera.set_iso(iso=str(CONFIGS[self.config][1]))  
        print("Changed config to %s %s" % CONFIGS[self.config])
        self.store_settings()
        return self.config

    def get_brightness_adj(self, filename):
        brightness = float(ImageAnalyzer.mean_brightness(filename))

        delta = BRIGHTNESS - brightness

        print("brightness is %d"% brightness)
        adjustment = int(round(math.log(BRIGHTNESS/brightness)/math.log(1.4)))
        print("%d, delta is %d"% (brightness, adjustment))

        if self.config + adjustment > len(CONFIGS) - 1:
            return len(CONFIGS)-1 - self.config
        elif self.config + adjustment  < 0:
            return -self.config

        return adjustment 

    def take_pic(self):
        self.filename = self.camera.capture_image_and_download()
        return self.filename

    def check_brightness(self, filename=None):
        filename = filename or self.filename
        config_delta = self.get_brightness_adj(filename)
        if config_delta != 0: 
            self.config = self.change_setting(config_delta)
            return self.config, False 
        return self.config, True

    def set_pic_store_dir(self, dirname):
        call(["mkdir", "-p", dirname])
        self.store_dirname = dirname

    def store_pic(self, dirname=None):
        if self.filename is not None:
            dirname = self.store_dirname or './'
            print(dirname)
            target_file = "%s/pic_%04d.jpg" % (dirname, self.pic_id)
            print("Storing file at %s" % target_file)
            os.rename(self.filename, target_file)
            self.pic_id += 1

    def store_settings(self):
         with open(self.config_file, 'w') as f:
             f.write(str(self.config))




