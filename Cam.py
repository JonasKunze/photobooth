# coding: utf-8

from gphoto import GPhoto
from gphoto import ImageAnalyzer 
import subprocess
import math
import os
import time
from subprocess import call
from gpiozero import LED

BRIGHTNESS = 112 

LED_HIGH_PIN = 13
LED_LOW_PIN = 26 

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
        ("1/30", 200),
        ("1/25", 200),
        ("1/40", 400),
        ("1/30", 400),
        ("1/25", 400),
        ("1/20", 400),
        ("1/30", 800),
        ("1/25", 800),
        ("1/20", 800),
        ("1/15", 800),
        ("1/13", 800),
        ("1/20", 1600),
        ("1/15", 1600),
        ("1/13", 1600),
        ("1/10", 1600),
        ]


class Cam():
    def __init__(self):
        self.config_file = ".cam-configs" 
        self.filename = None

        self.load_config()

        self.pic_id = 0
        while True:
            try:
                self.camera = GPhoto(subprocess)
                self.change_setting(0)
                break
            except Exception as e:  
                call(["pkill", "gvfs-gphoto2*"])
                call(["killall", "-9", "gvfsd-gphoto2"])
                print("Exception caught: {0}".format(e))
        self.active = True
        self.led_high = LED(LED_HIGH_PIN)
        self.led_low = LED(LED_LOW_PIN)
        self.led_high.on()
        self.led_low.on()

    def change_setting(self, delta):
        if self.config + delta > len(CONFIGS) - 1 or self.config + delta  < 0:
            return self.config

        self.config = self.config + delta
        self.camera.set_shutter_speed(secs=CONFIGS[self.config][0])

        self.camera.set_iso(CONFIGS[self.config][1])  
        print("Changed config to %s %s" % CONFIGS[self.config])
        self.store_settings()
        return self.config

    def set_brightness_leds(self, adjustment):
        self.led_low.off()
        self.led_high.off()
        if adjustment < 0:
            self.led_high.on()
        if adjustment > 0:
            self.led_low.on()

    def get_brightness_adj(self, filename):
        brightness = float(ImageAnalyzer.mean_brightness(filename))

        delta = self.brightness - brightness

        adjustment = int(round(math.log(self.brightness/brightness)/math.log(1.15)))
        print("brightness: %d, delta: %d"% (brightness, adjustment))

        self.led_low.off()
        self.led_high.off()
        if adjustment < 0:
            self.led_high.on()
        if adjustment > 0:
            self.led_low.on()

        if self.config + adjustment > len(CONFIGS) - 1:
            return len(CONFIGS)-1 - self.config
        elif self.config + adjustment  < 0:
            return -self.config

        return adjustment 

    def take_pic(self):
        self.led_low.on()
        self.led_high.on()
        self.filename = self.camera.capture_image_and_download()
        return self.filename

    def check_brightness(self, filename=None):
        filename = filename or self.filename
        config_delta = self.get_brightness_adj(filename)
        self.set_brightness_leds(config_delta)
        return config_delta

    def increase_brightness(self):
        print("increasing brightness")
        self.brightness += 8
        self.change_setting(1)

    def decrease_brightness(self):
        print("decreasing brightness")
        self.brightness -= 8
        self.change_setting(-1)

    def set_pic_store_dir(self, dirname):
        call(["mkdir", "-p", dirname])
        self.store_dirname = dirname

    def store_pic(self, dirname=None):
        if self.filename is not None:
            dirname = dirname or self.store_dirname 
            print(dirname)
            target_file = "%s/pic_%04d.jpg" % (dirname, self.pic_id)
            print("Storing file at %s" % target_file)
            try:
                os.rename(self.filename, target_file)
                print("success")
            except:
                print("Unable to store file at %s"%target_file)
                self.active = False
                quit()

            self.pic_id += 1
    def get_all_pics(self, dirname=None):
        dirname = dirname or self.store_dirname 
        code, out, err = self.camera.call(["find %s -name '*.jpg'|sort"%dirname])  
        return out.splitlines()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = int(f.readline())
                self.brightness = int(f.readline())
                print("Found cam config file: %d %d"%(self.config, self.brightness))
        except IOError:
            self.config = len(CONFIGS)/2
            self.brightness = BRIGHTNESS
            print("No cam config file found. Using default: %d %d"%(self.config, self.brightness))

    def store_settings(self):
         with open(self.config_file, 'w') as f:
             f.write("%d\n"%self.config)
             f.write(str(self.brightness))

    def is_active(self):
        return self.active

    def stop(self):
        self.active = False




