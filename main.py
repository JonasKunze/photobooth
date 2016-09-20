#!/usr/bin/python3
# coding: utf-8


from Display import Display 
from Cam import Cam 
from PIL import Image
from gpiozero import Button
from threading import Timer, Thread
import datetime
import time

resolution = (1440, 1050)

# time between pressing buzzer and the picture taken
BUZZER_DELAY = 2

# Time between take_pic() and the actual DSLR click
CLICK_DELAY = 0.25

BUZZER_PIN = 3
BUTTON_UP_PIN = 5
BUTTON_DOWN_PIN = 6

buzzer = Button(BUZZER_PIN)
button_up = Button(BUTTON_UP_PIN, bounce_time=0.1)
button_down = Button(BUTTON_DOWN_PIN, bounce_time=0.1)

date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
pics_dir = './pics'
output_dir = '%s/%s' % (pics_dir, date_str)

def cancel_timer(timer):
    if timer != None:
        try:
            timer.cancel()
        except:
            pass

def process_image(cam, filename):
    cam.check_brightness(filename)
    cam.store_pic(output_dir)

cam = Cam()
cam.set_pic_store_dir(output_dir)
button_up.when_pressed = cam.increase_brightness 
button_down.when_pressed = cam.decrease_brightness
with Display(resolution) as display:
    display.show_video_fullscreen()
    
#    with Image.open(".capture.jpg") as img:
#        display.show_image_fullscreen(img)

    show_video_small_timer = None
    show_history_timer = None

    def on_buzzer_pushed():
        print("buzzer pushed")
        global show_video_small_timer
        global show_history_timer
        cancel_timer(show_video_small_timer)
        cancel_timer(show_history_timer)
        show_video_small_timer = None
        show_history_timer = None

        display.show_video_fullscreen()

        time.sleep(BUZZER_DELAY or CLICK_DELAY - CLICK_DELAY)
        Timer(CLICK_DELAY, display.flash,()).start() 
        
        try:
            filename = cam.take_pic()
        except:
            cam.stop()
            return

        with Image.open(filename) as img:
            display.show_image_fullscreen(img)
            img_processor = Thread(target=process_image, args=(cam, filename))
            img_processor.start()

            show_video_small_timer = Timer(10, display.show_video_small, ())
            show_video_small_timer.start()

            show_history_timer = Timer(45, display.show_images_fullscreen, [cam.get_all_pics(pics_dir)])
            show_history_timer.start()


    buzzer.when_pressed = on_buzzer_pushed

#    on_buzzer_pushed()

    try:
        while cam.is_active():
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit) as e:
        cancel_timer(show_video_small_timer)
        cancel_timer(show_history_timer)
        print("Closing app")
