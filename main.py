# coding: utf-8

from Display import Display 
from Cam import Cam 
from PIL import Image
from gpiozero import LED, Button

import time
print("Starting!!")

resolution = (1680, 1050)

BUTTON_PIN = 3
button = Button(BUTTON_PIN)

cam = Cam()
with Display(resolution) as display:

    display.show_video_fullscreen()

    def on_buzzer_pushed():
        print("buzzer pushed")
        filename = cam.take_pic()
        filename = "capt0000.jpg"
        print("showing image %s" % filename)
        with Image.open(filename) as img:
            print("showing now")
            display.show_image_fullscreen(img)
            cam.check_brightness()

    button.when_pressed = on_buzzer_pushed
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt, SystemExit:
        print("Closing app")
