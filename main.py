#!/usr/bin/python 
# coding: utf-8


from Display import Display 
from Cam import Cam 
from PIL import Image
from gpiozero import LED, Button
from threading import Timer, Thread
import datetime

import time

#resolution = (1680, 1050)
resolution = (1280, 960)
resolution = (1260, 788)

# time between pressing buzzer and the picture taken
BUZZER_DELAY = 0

# Time between take_pic() and the actual DSLR click
CLICK_DELAY = 0.8

BUZZER_PIN = 3
BUTTON_UP_PIN = 5
BUTTON_DOWN_PIN = 6
LED_HIGH_PIN = 13
LED_LOW_PIN = 26 

buzzer = Button(BUZZER_PIN)
button_up = Button(BUTTON_UP_PIN, bounce_time=0.1)
button_down = Button(BUTTON_DOWN_PIN, bounce_time=0.1)
led_high = LED(LED_HIGH_PIN)
led_low = LED(LED_LOW_PIN)

def high_on():
    led_low.on()
def high_off():
    led_low.off()
led_high.on()
led_low.on()


date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
output_dir = './pics/%s' % date_str

def cancel_timer(timer):
    if timer != None:
        try:
            timer.cancel()
        except:
            pass

def set_brightness_leds(delta):
    led_low.off()
    led_high.off()
    if delta > 0:
        led_high.on()
    if delta < 0:
        led_low.on()


def process_image(cam, filename):
    delta = cam.check_brightness(filename)
    set_brightness_leds(delta)
    cam.store_pic(output_dir)

cam = Cam()
cam.set_pic_store_dir(output_dir)
button_up.when_pressed = cam.increase_brightness 
button_down.when_pressed = cam.decrease_brightness
with Display(resolution) as display:
#    display.show_video_fullscreen()

    filename = "pic_0000.jpg"

    show_video_small_timer = None

    def on_buzzer_pushed():
        print("buzzer pushed")
        global show_video_small_timer
        cancel_timer(show_video_small_timer)
        show_video_small_timer = None

        display.show_video_fullscreen()

        time.sleep(BUZZER_DELAY or CLICK_DELAY - CLICK_DELAY)
        Timer(CLICK_DELAY, display.flash,()).start() 
        
        filename = cam.take_pic()

        with Image.open(filename) as img:
            display.show_image_fullscreen(img)
            img_processor = Thread(target=process_image, args=(cam, filename))
            img_processor.start()

            show_video_small_timer = Timer(5, display.show_video_small, ())
            show_video_small_timer.start()


    buzzer.when_pressed = on_buzzer_pushed

    on_buzzer_pushed()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt, SystemExit:
        cancel_timer(show_video_small_timer)
        print("Closing app")
