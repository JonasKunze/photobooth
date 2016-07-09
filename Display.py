# coding: utf-8

from picamera import PiCamera
import io
import time
import numpy as np
from threading import Timer
from random import randint


from PIL import Image
from time import sleep

SMALL_VIDEO_TOGGLE_TIME = 10


BACKGROUND = 10
FOREGROUND = 100

class Display(PiCamera):
    def __init__(self, size):
        PiCamera.__init__(self) 
        self.size = size
        self.resolution = size 
        self.framerate = 25 
        self.rotation = -90
        self.hflip = True
        self.all_overlays = [None]*FOREGROUND*2 
        self.previewing_small = False
        self.current_small_window_id = -1
        self.toggle_timer = None

        #small window
        self.small_window_size = (640, 480)
        self.small_window_area = (150, 0, self.size[0] - self.small_window_size[0], self.size[1] - self.small_window_size[1])

    def start_preview(self):
        if self.previewing == False:
            super(Display, self).start_preview()

    def remove_layer(self, layer):
        if self.all_overlays[layer] is not None:
            self.remove_overlay(all_overlays[layer])
            self.all_overlays[layer] = None

    def show_video_fullscreen(self, layer=BACKGROUND):
        self.remove_layer(layer)

        self.start_preview()
        self.preview.fullscreen = True
        self.preview.layer = layer 
        self.previewing_small = False

    def toggle_small_video_position(self):
        if self.previewing_small == True and self.closed == False:
            x = randint(self.small_window_area[0], self.small_window_area[2]) 
            y = randint(self.small_window_area[1], self.small_window_area[3]) 
            self.preview.window = (x, y, self.small_window_size[0], self.small_window_size[1]) 
            self.toggle_timer = Timer(SMALL_VIDEO_TOGGLE_TIME, self.toggle_small_video_position, ())
            self.toggle_timer.start()

    def show_video_small(self, layer=FOREGROUND):
        self.start_preview()
        self.preview.fullscreen = False 
        self.preview.layer = layer 
        self.previewing_small = True 
        self.toggle_small_video_position()

    def hide_video(self):
        self.previewing_small = False 
        super(Display, self).stop_preview()

    def show_image_fullscreen(self, image, layer=BACKGROUND, minimize_video=False):
        self.show_image(image, BACKGROUND, True)
        if self.previewing == True and minimize_video == True:
            self.show_video_small()
        else:
            self.hide_video()

    def show_image_small(self, image, layer=FOREGROUND):
        if self.previewing == True:
            self.show_video_fullscreen()
        self.show_image(image, layer, False, self.small_window)

    def show_image(self, img, layer, fullscreen, window=None):
        if self.all_overlays[layer] is not None:
            self.remove_layer(layer)

        pad = img 
        # make sure the image has the right size and is in RGB mode
        scale = 1
        if img.size[0] > self.size[0]:
            scale = self.size[0] / float(img.size[0])
        if img.size[1] > self.size[0]:
            yscale = self.size[1] / float(img.size[1])
            if yscale > scale:
                scale = yscale

        scaled_size = (int(img.size[0] * scale), int(img.size[1] * scale))
        img = img.resize(scaled_size)

        pad = Image.new("RGB", (
            ((img.size[0] + 31) // 32) * 32,
            ((img.size[1] + 15) // 16) * 16,
            ))
        margin = ((self.size[0] - scaled_size[0])/2, (self.size[1] - scaled_size[1])/2)
        pad.paste(img, margin)

        overlay = self.add_overlay(pad.tostring(), scaled_size)
        self.all_overlays[layer] = overlay
        overlay.fullscreen = fullscreen 

    def flash(self):
        layer = BACKGROUND+1
        image = Image.new("RGB", self.size, (255, 255, 255))
        self.show_image(image, layer, True)

        alpha = 255
        while self.overlay.alpha > 2:
            alpha = alpha/1.02
            self.overlay.alpha = int(alpha) 
            time.sleep(0.01)
        self.remove_layer(layer)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Shutting down the Display")
        if self.toggle_timer is not None:
            print("Canceling toggle timer")
            self.toggle_timer.cancel()
            print("done")
        super(Display, self).__exit__(exc_type, exc_value, traceback)
        

def test_display():
    with Display((1680, 1050)) as camera:

        # Load the arbitrarily sized image
#        img = Image.open('overlay.png')

        camera.show_video_fullscreen()
#        camera.show_image_fullscreen(img)
        camera.stop_preview()
#        camera.show_image_small(img)
        camera.show_video_small()
        camera.show_video_fullscreen()
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt, SystemExit:
            print("Closing app")
#test_display()
