import itertools
import os
import socket
import time

import smbus
from PIL import Image, ImageDraw, ImageFont

from . import SSD1306

show = SSD1306.SSD1306()
show.Init()
dir_path = os.path.dirname(os.path.abspath(__file__))

font_path = dir_path + '/font.ttf'

font_small = ImageFont.truetype(font_path, 13)
font_large = ImageFont.truetype(font_path, 26)

image1 = Image.new('1', (show.width, show.height), "WHITE")
draw = ImageDraw.Draw(image1)

DEFAULT_TEMP_THRESHOLD_FOR_FAN = 30
DEFAULT_DISPLAY_DELAY_SECONDS = 2


class POE_HAT_B:
    def __init__(self, address=0x20, temp_threshold_for_fan=DEFAULT_TEMP_THRESHOLD_FOR_FAN,
                 display_delay=DEFAULT_DISPLAY_DELAY_SECONDS):
        self.i2c = smbus.SMBus(1)
        self.address = address  # 0x20

        self.display_delay = display_delay
        self.fan_enabled = True
        self.enable_fan()
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

    def date_time_view(self):
        self.display_two_lines(
            time.strftime('%Y-%m-%d', time.localtime()),
            time.strftime('%H:%M:%S', time.localtime())
        )

    def time_single_line_view(self):
        self.display_one_line(
            time.strftime('%H:%M:%S', time.localtime())
        )

    def load_average_view(self):
        load1, load5, load15 = os.getloadavg()
        self.display_two_lines(
            f"load average:",
            f"1m: {load1:.2f} | 5m: {load5:.2f} | 15m: {load15:.2f}"
        )

    def temp_and_fan_view(self):
        temp = self.retrieve_temperature()

        if temp >= self.temp_threshold_for_fan:
            self.enable_fan()
        elif temp < self.temp_threshold_for_fan - 2:
            self.disable_fan()

        temp_formatted_line = f"cpu: {temp:.1f}°C"
        fan_status_line = "fan: enabled" if self.fan_enabled else "fan: disabled"

        self.display_two_lines(temp_formatted_line, fan_status_line)

    def address_and_host_view(self):
        self.display_two_lines(
            f"host: {self.hostname}",
            f"ip: {self.ip}",
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
        draw.text((0, 18), line2, font=font_small, fill=0)
        show.ShowImage(show.getbuffer(img))

    def display(self):
        for view in itertools.cycle([
            self.time_single_line_view,
            self.address_and_host_view,
            self.date_time_view,
            self.temp_and_fan_view,
            self.load_average_view,
        ]):
            view()
            time.sleep(self.display_delay)
