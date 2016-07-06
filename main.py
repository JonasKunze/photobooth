# coding: utf-8

from Display import Display 
from Cam import Cam 
from PIL import Image
import time

resolution = (1680, 1050)

cam = Cam()
with Display(resolution) as camera:

    # Load the arbitrarily sized image
    #img = Image.open('overlay.png')

    camera.show_video_fullscreen()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt, SystemExit:
        print("Closing app")
