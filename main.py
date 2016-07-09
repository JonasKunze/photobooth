# coding: utf-8

from Display import Display 
from Cam import Cam 
from PIL import Image
from gpiozero import LED, Button
from threading import Timer
import datetime

import time

resolution = (1280, 960)
resolution = (1680, 1050)
buzzer_delay = 0

BUTTON_PIN = 3
button = Button(BUTTON_PIN)

date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
output_dir = './pics/%s' % date_str

def cancel_timer(timer):
    if timer != None:
        try:
            timer.cancel()
        except:
            pass

cam = Cam()
cam.set_pic_store_dir(output_dir)
with Display(resolution) as display:

    display.show_video_small()
    display.show_video_fullscreen()

    filename = "capt0000.jpg"

    show_video_small_timer = None
    show_video_fullscreen_timer = None
    def on_buzzer_pushed():
        global show_video_small_timer
        global show_video_fullscreen_timer
        cancel_timer(show_video_small_timer)
        cancel_timer(show_video_fullscreen_timer)
        show_video_fullscreen_timer = None

        display.show_video_fullscreen()
        print("buzzer pushed")
        time.sleep(buzzer_delay)
        filename = cam.take_pic()
        print("showing image %s" % filename)
        with Image.open(filename) as img:
            print("showing now")
            display.show_image_fullscreen(img)
            cam.check_brightness(filename)
            show_video_small_timer = Timer(2, display.show_video_small, ()).start()
            cam.store_pic(output_dir)

    button.when_pressed = on_buzzer_pushed

    on_buzzer_pushed()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt, SystemExit:
        print("Closing app")
