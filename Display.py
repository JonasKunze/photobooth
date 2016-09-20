# coding: utf-8

from picamera import PiCamera
import io
import time
import numpy as np
from threading import Timer
from random import randint


from PIL import Image
from time import sleep

SMALL_VIDEO_TOGGLE_TIME = 5 
FULLSCREEN_IMAGE_TOGGLE_TIME = 10 


BACKGROUND = 1
FOREGROUND = 3

class Display(PiCamera):
    def __init__(self, size):
        PiCamera.__init__(self) 
        self.size = size
        self.resolution = size 
        self.framerate = 25 
        self.rotation = -90
        self.hflip = True
        self.all_overlays = [None]*FOREGROUND*2 
        self.toggle_timers = [None]*len(self.all_overlays) 
        self.previewing_small = False
        self.current_small_window_id = -1
        self.zoom=(0.1, 0.1, 1, 1)
        self.fullscreen_window = (176, -3, self.size[0], self.size[1]) 
        self.is_flashing = False

        #small window
        self.small_window_size = (int(size[0]/2.8), int(size[1]/2.8))
        self.small_window_area = (175, -3, self.size[0] - self.small_window_size[0], self.size[1] - self.small_window_size[1])

    def start_preview(self):
        if self.previewing == True:
            self.clear_layer(self.preview.layer)

        if self.previewing == False:
            super(Display, self).start_preview()

    def clear_layer(self, layer):
        timer = self.toggle_timers[layer]
        if timer is not None:
            timer.cancel()
            self.toggle_timers[layer] = None
        if self.all_overlays[layer] is not None:
            print("Clearing layer %d"%layer)
            self.remove_overlay(self.all_overlays[layer])
            self.all_overlays[layer] = None


    def show_video_fullscreen(self, layer=BACKGROUND):
        self.clear_layer(layer)

        self.start_preview()
        self.preview.fullscreen =False 
        self.preview.layer = layer 

        # correction for weird vga display
        self.preview.window = self.fullscreen_window 
        self.previewing_small = False
        print("Showing fullscreen video on layer %d"%layer)

    def toggle_small_window_position(self, overlay):
        timer = self.toggle_timers[overlay.layer]
        if timer is not None:
            timer.cancel()

        if self.closed == False:
            x = randint(self.small_window_area[0], self.small_window_area[2]) 
            y = randint(self.small_window_area[1], self.small_window_area[3]) 
            overlay.window = (x, y, self.small_window_size[0], self.small_window_size[1]) 
            print("toggling small window on layer %d to %s"%(overlay.layer, overlay.window))

            timer = self.toggle_timers[overlay.layer] = Timer(SMALL_VIDEO_TOGGLE_TIME, self.toggle_small_window_position, [overlay])
            self.toggle_timers[overlay.layer] = timer
            timer.start()

    def show_video_small(self, layer=FOREGROUND):
        self.clear_layer(layer)

        self.start_preview()
        self.preview.fullscreen = False 
        self.preview.layer = layer 
        self.previewing_small = True 
        self.toggle_small_window_position(self.preview)
        print("Showing small video on layer %d"%layer)

    def hide_video(self):
        print("hiding video")
        self.previewing_small = False 
        super(Display, self).stop_preview()
        if self.preview is not None:
            self.clear_layer(self.preview.layer)

    def show_images_fullscreen(self, image_paths, layer=BACKGROUND, minimize_hide_or_keep_video='hide'):
        timer = self.toggle_timers[layer]
        if timer is not None:
            timer.cancel()
        with Image.open(image_paths[randint(0, len(image_paths)-1)]) as image: 
            self.show_image_fullscreen(image, layer, 'hide')

        timer = self.toggle_timers[layer] = Timer(FULLSCREEN_IMAGE_TOGGLE_TIME, self.show_images_fullscreen, (image_paths, layer, minimize_hide_or_keep_video))
        self.toggle_timers[layer] = timer
        timer.start()

    def show_image_fullscreen(self, image, layer=BACKGROUND, minimize_hide_or_keep_video='hide'):
        overlay = self.show_image(image, layer, self.size)
        overlay.window = self.fullscreen_window

        if self.previewing == True:
            if minimize_hide_or_keep_video == 'minimize':    
                self.show_video_small()
            elif minimize_hide_or_keep_video == 'hide':
                self.hide_video()
        print("Showing fullscreen image on layer %d"%layer)
        return overlay

    def show_image_small(self, image, layer=FOREGROUND):
        if self.previewing == True:
            self.show_video_fullscreen()

        overlay = self.show_image(image, layer, self.small_window_size)
        self.toggle_small_window_position(overlay)
        print("Showing small image on layer %d"%layer)
        return overlay

    def show_image(self, img, layer, size):
        size = ( 
                    (size[0] // 32) * 32,
                    (size[1] // 16) * 16,
                )


        # make sure the image has the right size and is in RGB mode
        scale = 1
        if img.size[0] > size[0]:
            scale = size[0] / float(img.size[0])
        if img.size[1] > size[0]:
            yscale = size[1] / float(img.size[1])
            if yscale > scale:
                scale = yscale

        scaled_size = (int(img.size[0] * scale), int(img.size[1] * scale))
        img = img.resize(scaled_size)

        margin = (int((img.size[0] - size[0])/2), int((img.size[1] - size[1])/2))
        img = img.crop((margin[0], margin[1], img.size[0]-margin[0], img.size[1]-margin[1]))

        self.clear_layer(layer)

        overlay = self.add_overlay(img.tostring(), img.size)
        self.all_overlays[layer] = overlay
        overlay.layer = layer
        overlay.fullscreen = False
        return overlay

    def flash(self):
        if self.is_flashing == True:
            return
        self.is_flashing = True

        print("flashing")
        layer = 5 
        image = Image.new("RGB", self.size, (255, 255, 255))
        overlay = self.show_image_fullscreen(image, layer, 'keep')

        alpha = 255
        overlay.alpha = alpha
        while alpha > 0.5:
            alpha = alpha/1.1
            overlay.alpha = int(alpha) 
            sleep(0.07)
        self.clear_layer(layer)
        self.is_flashing = False 

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Shutting down the Display")
        for timer in self.toggle_timers:
            if timer is not None:
                print("Canceling toggle timer")
                timer.cancel()

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
        except (KeyboardInterrupt, SystemExit) as e:
            print("Closing app")
#test_display()
