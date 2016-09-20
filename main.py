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
BUTTON_NEXT = 10
BUTTON_PREV = 11

buzzer = Button(BUZZER_PIN)
button_up = Button(BUTTON_UP_PIN, bounce_time=0.1)
button_down = Button(BUTTON_DOWN_PIN, bounce_time=0.1)
button_next = Button(BUTTON_NEXT, bounce_time=0.1)
button_prev = Button(BUTTON_PREV, bounce_time=0.1)

date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
pics_dir = './pics'
output_dir = '%s/%s' % (pics_dir, date_str)

pic_shown = -1 

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


    def on_next_pushed():
        print("next pushed")
        global show_video_small_timer
        global show_history_timer
        global pic_shown
        cancel_timer(show_video_small_timer)
        cancel_timer(show_history_timer)
        show_video_small_timer = None
        show_history_timer = None

        images = cam.get_all_pics(pics_dir)
        if pic_shown > -1:
            if pic_shown < len(images) - 1:
                pic_shown = pic_shown + 1
            else:
                pic_shown = -1
                display.show_video_fullscreen()
        if pic_shown > -1 and len(images) > 0: 
            with Image.open(cam.get_all_pics(pics_dir)[pic_shown]) as image:
                display.show_image_fullscreen(image)

    def on_prev_pushed():
        print("prev pushed")
        global show_video_small_timer
        global show_history_timer
        global pic_shown
        cancel_timer(show_video_small_timer)
        cancel_timer(show_history_timer)
        show_video_small_timer = None
        show_history_timer = None

        images = cam.get_all_pics(pics_dir)
        if pic_shown > 0:
            pic_shown = pic_shown - 1
        else:
            pic_shown = len(images) - 1
        if len(images) > 0:
            with Image.open(cam.get_all_pics(pics_dir)[pic_shown]) as image:
                display.show_image_fullscreen(image)
 

    buzzer.when_pressed = on_buzzer_pushed
    button_next.when_pressed = on_next_pushed
    button_prev.when_pressed = on_prev_pushed

    on_next_pushed()
#    on_buzzer_pushed()

    try:
        while cam.is_active():
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit) as e:
        cancel_timer(show_video_small_timer)
        cancel_timer(show_history_timer)
        print("Closing app")
