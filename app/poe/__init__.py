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

font_path = dir_path + '/font.ttf'

font_small = ImageFont.truetype(font_path, 15)
font_large = ImageFont.truetype(font_path, 30)

image1 = Image.new('1', (show.width, show.height), "WHITE")
draw = ImageDraw.Draw(image1)

DEFAULT_TEMP_THRESHOLD_FOR_FAN = 30

class POE_HAT_B:
    def __init__(self, address=0x20, temp_threshold_for_fan=DEFAULT_TEMP_THRESHOLD_FOR_FAN):
        self.i2c = smbus.SMBus(1)
        self.address = address  # 0x20
        self.enable_fan()
        self.FAN_MODE = 0
        self.fan_enabled = False
        self.TEMP_THRESHOLD_FOR_FAN = 40
        self.temp_threshold_for_fan = temp_threshold_for_fan
        self.hostname = socket.gethostname()
        self.ip = self.retrieve_ip_address()

    def enable_fan(self):
        self.fan_enabled = True
        self.i2c.write_byte(self.address, 0xFE & self.i2c.read_byte(self.address))

    def disable_fan(self):
        self.fan_enabled = False
        self.i2c.write_byte(self.address, 0x01 | self.i2c.read_byte(self.address))

    def retrieve_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def retrieve_temperature(self):
        with open('/sys/class/thermal/thermal_zone0/temp', 'rt') as f:
            temp = (int)(f.read()) / 1000.0
        return temp

    def POE_HAT_Display(self):
        # show.Init()
        # show.ClearBlack()

        image1 = Image.new('1', (show.width, show.height), "WHITE")
        draw = ImageDraw.Draw(image1)
        ip = self.retrieve_ip_address()
        temp = self.retrieve_temperature()
        draw.text((0, 1), 'IP:' + str(ip), font=font_small, fill=0)
        draw.text((0, 15), 'Temp:' + str(((int)(temp * 10)) / 10.0), font=font_small, fill=0)

        if temp >= self.temp_threshold_for_fan:
            self.FAN_MODE = 1
            self.enable_fan()
            self.fan_enabled = True
        elif temp < self.temp_threshold_for_fan - 2:
            self.FAN_MODE = 0
            self.disable_fan()
            self.fan_enabled = False

        if (self.FAN_MODE == 1):
            draw.text((77, 16), 'FAN:ON', font=font_small, fill=0)
            self.enable_fan()
        else:
            draw.text((77, 16), 'FAN:OFF', font=font_small, fill=0)
            self.disable_fan()
        show.ShowImage(show.getbuffer(image1))

    def date_time_view(self):
        self.display_two_lines(
            'date: ' + time.strftime('%Y-%m-%d', time.localtime()),
            'time: ' + time.strftime('%H:%M:%S', time.localtime())
        )

    def date_time_single_line_view(self):
        self.display_one_line(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        )

    def temp_and_fan_view(self):
        temp = self.retrieve_temperature()

        if temp >= self.temp_threshold_for_fan:
            self.enable_fan()
        elif temp < self.temp_threshold_for_fan - 2:
            self.disable_fan()

        temp_formatted_line = f"cpu temperature: {temp:.1f}°C"
        # temp_formatted_line = f"cpu temperature: " + str(((int)(temp * 10)) / 10.0) + "°C"
        fan_status_line = "fan:  on" if self.fan_enabled else "fan: off"

        self.display_two_lines(temp_formatted_line, fan_status_line)

    def address_and_host_view(self):
        self.display_two_lines(
            f"ip:   {self.ip}",
            f"host: {self.hostname}"
        )

    def display_one_line(self, text):
        img = Image.new('1', (show.width, show.height), "WHITE")
        draw = ImageDraw.Draw(img)
        draw.text((0, 1), text, font=font_large, fill=0)
        show.ShowImage(show.getbuffer(img))

    def display_two_lines(self, line1, line2):
        img = Image.new('1', (show.width, show.height), "WHITE")
        draw = ImageDraw.Draw(img)
        draw.text((0, 1), line1, font=font_small, fill=0)
        draw.text((0, 15), line2, font=font_small, fill=0)
        show.ShowImage(show.getbuffer(img))

    def display(self):
        views = [
            self.address_and_host_view,
            self.temp_and_fan_view,
            self.date_time_view,
            self.date_time_single_line_view,
        ]

        for view in itertools.cycle(views):
            view()
            time.sleep(1)
