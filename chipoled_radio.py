#!/usr/bin/python
 
import os
import sys
import CHIP_IO.GPIO as GPIO
import time
import subprocess
 
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
 
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)
 
#font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'fonts','FreePixel.ttf'))
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
font_path_cnc = os.path.abspath(os.path.join(os.path.dirname(__file__),'fonts','C&C Red Alert [INET].ttf'))
 
font = ImageFont.truetype(font_path, 16)
font1 = ImageFont.truetype(font_path, 12)
 
_next = "XIO-P7"
_prev = "XIO-P4"
_up   = "XIO-P5"
_down = "XIO-P6"
_shut = "XIO-P3"
 
GPIO.setup(_next, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(_prev, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(_up,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(_shut, GPIO.IN, pull_up_down=GPIO.PUD_UP)
 
vol = 50
channel_num = 0
channel_name = "OFF"
 
channel_file = os.path.abspath(os.path.join(os.path.dirname(__file__),"channel.txt"))
channel = open(channel_file,"r")
channel_arr = channel.readlines()
channel_count = len(channel_arr)
 
def show_radio() :
  global channel_name, channel_num
  with canvas(device) as draw:
    pos = 128 * vol / 100
    draw.rectangle((0, 55, 127, 63), outline="white", fill="black")
    draw.rectangle((0, 55, pos, 63), outline="white", fill="white")
    draw.text((0,0), "Channel : "+str(channel_num+1), font=font1, fill="white")
    draw.text((0,22), channel_name, font=font, fill="white")
 
def change_volume(nomor) :
  subprocess.Popen(["amixer","-c","0","sset","Power Amplifier",str(nomor)+"%"])
  show_radio()
 
def change_channel(nomor) :
    global channel_name, channel_detail, channel_num
    if not channel_arr[nomor].strip() :
      channel_num = 0
      change_channel(channel_num)
    else :
      channel_detail = channel_arr[nomor].split(";")
      print "Nama:", channel_detail[0]
      print "URL :", channel_detail[1]
      subprocess.Popen(["mpc", "stop"])
      subprocess.Popen(["mpc", "clear"])
      subprocess.Popen(["mpc", "add", channel_detail[1].strip()])
      subprocess.Popen(["mpc", "play"])
      channel_name = channel_detail[0].strip()
      show_radio()
 
change_volume(vol)
change_channel(0)
 
while True:
  if GPIO.input(_up) == 0 :
    vol += 10
    if vol > 100 :
      vol = 100
    change_volume(vol)
 
  if GPIO.input(_down) == 0 :
    vol -= 10
    if vol < 0 :
      vol = 0
    change_volume(vol)
 
  if GPIO.input(_prev) == 0 :
    channel_num -= 1
    if channel_num < 0 :
      channel_num = channel_count-1
    change_channel(channel_num)
 
  if GPIO.input(_next) == 0 :
    channel_num += 1
    if channel_num > channel_count-1 :
      channel_num = 0
    change_channel(channel_num)
 
  if GPIO.input(_shut) == 0 :
    with canvas(device) as draw:
      draw.text((0,0), "Shutting down...", font=font1, fill="white")
    subprocess.Popen(['mpc','stop'])
    subprocess.Popen(['mpc','clear'])
    GPIO.cleanup()
    #subprocess.call("sudo poweroff", shell=True)
    exit()
 
  time.sleep(0.05)
GPIO.cleanup()
