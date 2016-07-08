# coding: utf-8

from Display import Display 
from Cam import Cam 
from PIL import Image
from gpiozero import LED, Button
from threading import Timer

import time

resolution = (1280, 960)
resolution = (1680, 1050)

BUTTON_PIN = 3
button = Button(BUTTON_PIN)


cam = Cam()
with Display(resolution) as display:

    display.show_video_fullscreen()
    filename = "capt0000.jpg"
    cam.check_brightness(filename)

    def on_buzzer_pushed():
        display.show_video_fullscreen()
        print("buzzer pushed")
        filename = cam.take_pic()
        print("showing image %s" % filename)
        with Image.open(filename) as img:
            print("showing now")
            display.show_image_fullscreen(img)
            cam.check_brightness()
            Timer(10, display.show_video_small, ()).start()
            Timer(30, display.show_video_fullscreen, ()).start()

    button.when_pressed = on_buzzer_pushed
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt, SystemExit:
        print("Closing app")
