import os
import socket
import time
import itertools
import smbus
from PIL import Image, ImageDraw, ImageFont

from . import SSD1306

show = SSD1306.SSD1306()
show.Init()
dir_path = os.path.dirname(os.path.abspath(__file__))

font = ImageFont.truetype(dir_path + '/font.ttf', 14)

image1 = Image.new('1', (show.width, show.height), "WHITE")
draw = ImageDraw.Draw(image1)


class POE_HAT_B:
    def __init__(self, address=0x20):
        self.i2c = smbus.SMBus(1)
        self.address = address  # 0x20
        self.FAN_ON()
        self.FAN_MODE = 0
        self.FAN_TEMP = 40

    def FAN_ON(self):
        self.i2c.write_byte(self.address, 0xFE & self.i2c.read_byte(self.address))

    def FAN_OFF(self):
        self.i2c.write_byte(self.address, 0x01 | self.i2c.read_byte(self.address))

    def GET_IP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def GET_Temp(self):
        with open('/sys/class/thermal/thermal_zone0/temp', 'rt') as f:
            temp = (int)(f.read()) / 1000.0
        return temp

    def POE_HAT_Display(self):
        # show.Init()
        # show.ClearBlack()

        image1 = Image.new('1', (show.width, show.height), "WHITE")
        draw = ImageDraw.Draw(image1)
        ip = self.GET_IP()
        temp = self.GET_Temp()
        draw.text((0, 1), 'IP:' + str(ip), font=font, fill=0)
        draw.text((0, 15), 'Temp:' + str(((int)(temp * 10)) / 10.0), font=font, fill=0)
        if (temp >= self.FAN_TEMP):
            self.FAN_MODE = 1

        elif (temp < self.FAN_TEMP - 2):
            self.FAN_MODE = 0

        if (self.FAN_MODE == 1):
            draw.text((77, 16), 'FAN:ON', font=font, fill=0)
            self.FAN_ON()
        else:
            draw.text((77, 16), 'FAN:OFF', font=font, fill=0)
            self.FAN_OFF()
        show.ShowImage(show.getbuffer(image1))

    def show_datetime(self):
        img = Image.new('1', (show.width, show.height), "WHITE")
        draw = ImageDraw.Draw(img)
        draw.text((0, 1), time.strftime('%Y-%m-%d', time.localtime()), font=font, fill=0)
        draw.text((0, 15), time.strftime('%H:%M:%S', time.localtime()), font=font, fill=0)
        show.ShowImage(show.getbuffer(img))

    def show_shrug(self):
        img = Image.new('1', (show.width, show.height), "WHITE")
        draw = ImageDraw.Draw(img)
        draw.text((0, 1), '¯\_(ツ)_/¯', font=font, fill=0)
        show.ShowImage(show.getbuffer(img))

    def show_smile(self):
        img = Image.new('1', (show.width, show.height), "WHITE")
        draw = ImageDraw.Draw(img)
        draw.text((0, 1), '(づ｡◕‿‿◕｡)づ', font=font, fill=0)
        show.ShowImage(show.getbuffer(img))

    def show_hostname(self):
        img = Image.new('1', (show.width, show.height), "WHITE")
        draw = ImageDraw.Draw(img)
        draw.text((0, 1), socket.gethostname(), font=font, fill=0)
        show.ShowImage(show.getbuffer(img))


    def display(self):
        views = [self.show_hostname, self.show_smile, self.POE_HAT_Display, self.show_datetime, self.show_shrug]

        for view in itertools.cycle(views):
            view()
            time.sleep(0.5)
