# -*- coding: utf-8 -*-
"""
Compiled, mashed and generally mutilated 2014-2015 by Denis Pleic
Made available under GNU GENERAL PUBLIC LICENSE

# Modified Python I2C library for Raspberry Pi
# as found on http://www.recantha.co.uk/blog/?p=4849
# Joined existing 'i2c_lib.py' and 'lcddriver.py' into a single library
# added bits and pieces from various sources
# By DenisFromHR (Denis Pleic)
# 2015-02-10, ver 0.1

# Modified for Vietnamese charset
# By Dang Huynh Anh (Babyze)
# 16/11/2021, ver 1.0
"""
#
import smbus
from time import *


class i2c_device:
    def __init__(self, addr, port=0):
        self.addr = addr
        self.bus = smbus.SMBus(port)

# Write a single command
    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        sleep(0.0001)

# Write a command and argument
    def write_cmd_arg(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        sleep(0.0001)

# Write a block of data
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        sleep(0.0001)

# Read a single byte
    def read(self):
        return self.bus.read_byte(self.addr)

# Read
    def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)

# Read a block of data
    def read_block_data(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)


# LCD Address
ADDRESS = 0x27

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit


class lcd:
    # initializes objects and lcd
    def __init__(self):
        self.lcd_device = i2c_device(ADDRESS)
        self.font = []

        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)

        self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE |
                       LCD_5x8DOTS | LCD_4BITMODE)
        self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        sleep(0.2)

    # clocks EN to latch command

    def lcd_strobe(self, data):
        self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
        sleep(.0005)
        self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
        sleep(.0001)

    def lcd_write_four_bits(self, data):
        self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
        self.lcd_strobe(data)

    # write a command to lcd
    def lcd_write(self, cmd, mode=0):
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

    # write a character to lcd (or character rom) 0x09: backlight | RS=DR<
    # works!
    def lcd_write_char(self, charvalue, mode=1):
        self.lcd_write_four_bits(mode | (charvalue & 0xF0))
        self.lcd_write_four_bits(mode | ((charvalue << 4) & 0xF0))

    # put string function

    def lcd_display_string(self, string, line):
        if line == 1:
            self.font = []
        string, self.font = self.process_unicode_string(string, self.font)
        self.lcd_load_custom_chars(self.font)

        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)
        if line == 3:
            self.lcd_write(0x94)
        if line == 4:
            self.lcd_write(0xD4)

        for char in string:
            self.lcd_write(ord(char), Rs)

    # clear lcd and set to home
    def lcd_clear(self):
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_RETURNHOME)

    # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
    def backlight(self, state):  # for state, 1 = on, 0 = off
        if state == 1:
            self.lcd_device.write_cmd(LCD_BACKLIGHT)
        elif state == 0:
            self.lcd_device.write_cmd(LCD_NOBACKLIGHT)

    # add custom characters (0 - 7)
    def lcd_load_custom_chars(self, fontdata):
        self.lcd_write(0x40)
        for char in fontdata:
            for line in char:
                self.lcd_write_char(line)

    # define precise positioning (addition from the forum)
    def lcd_display_string_pos(self, string, line, pos):
        if line == 1:
            self.font = []
        string, self.font = self.process_unicode_string(string, self.font)
        self.lcd_load_custom_chars(self.font)

        if line == 1:
            pos_new = pos
        elif line == 2:
            pos_new = 0x40 + pos
        elif line == 3:
            pos_new = 0x14 + pos
        elif line == 4:
            pos_new = 0x54 + pos

        self.lcd_write(0x80 + pos_new)

        for char in string:
            self.lcd_write(ord(char), Rs)

    # process unicode string
    def process_unicode_string(self, string, font):
        for char in string:
            if char in self.vietnamese_charset:
                try:
                    index = font.index(self.vietnamese_charset[char])
                except ValueError:
                    font.append(self.vietnamese_charset[char])
                    index = len(font) - 1

                string = string.replace(char, chr(index))
        return string, font

    vietnamese_charset = {
        "á": [
            0b00010,
            0b00100,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111,
            0b00000
        ],
        "à": [
            0b01000,
            0b00100,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111,
            0b00000
        ],
        "ả": [
            0b00100,
            0b00010,
            0b00100,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ã": [
            0b01101,
            0b10010,
            0b00000,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ạ": [
            0b00000,
            0b00000,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111,
            0b00100
        ],
        "Á": [
            0b00010,
            0b00100,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b10001
        ],
        "À": [
            0b01000,
            0b00100,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b10001
        ],
        "Ả": [
            0b00100,
            0b00010,
            0b00100,
            0b01110,
            0b10001,
            0b11111,
            0b10001,
            0b10001
        ],
        "Ã": [
            0b01101,
            0b10010,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b10001
        ],
        "Ạ": [
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b10001,
            0b00100

        ],
        "ă": [
            0b10001,
            0b01110,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111,
            0b00000
        ],
        "ắ": [
            0b00010,
            0b10101,
            0b01110,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ẳ": [
            0b01000,
            0b10101,
            0b01110,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ẵ": [
            0b01010,
            0b10101,
            0b01110,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ặ": [
            0b10001,
            0b01110,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111,
            0b00100
        ],
        "Ă": [
            0b10001,
            0b01110,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b00000
        ],
        "Ắ": [
            0b00010,
            0b10101,
            0b01110,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001
        ],
        "Ằ": [
            0b01000,
            0b10101,
            0b01110,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001
        ],
        "Ẳ": [
            0b00100,
            0b00010,
            0b10101,
            0b01110,
            0b01110,
            0b10001,
            0b11111,
            0b10001
        ],
        "Ẵ": [
            0b01101,
            0b10010,
            0b11111,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001
        ],
        "Ặ": [
            0b10001,
            0b01110,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b00100
        ],
        "â": [
            0b01110,
            0b10001,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111,
            0b00000
        ],
        "ấ": [
            0b00010,
            0b01110,
            0b10001,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ầ": [
            0b01000,
            0b01110,
            0b10001,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ẩ": [
            0b00100,
            0b00010,
            0b01110,
            0b11111,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ẫ": [
            0b01101,
            0b10010,
            0b01110,
            0b11111,
            0b00001,
            0b01111,
            0b10001,
            0b01111
        ],
        "ậ": [
            0b01110,
            0b10001,
            0b01110,
            0b00001,
            0b01111,
            0b10001,
            0b01111,
            0b00100
        ],
        "Â": [
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b00000
        ],
        "Ấ": [
            0b00010,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001
        ],
        "Ầ": [
            0b01000,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001
        ],
        "Ẩ": [
            0b00110,
            0b00010,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b11111,
            0b10001
        ],
        "Ẫ": [
            0b01101,
            0b10010,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b11111,
            0b10001
        ],
        "Ậ": [
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b11111,
            0b10001,
            0b00100
        ],
        "đ": [
            0b00010,
            0b00111,
            0b00010,
            0b01110,
            0b10010,
            0b10010,
            0b01110,
            0b00000
        ],
        "Đ": [
            0b01110,
            0b01001,
            0b01001,
            0b11101,
            0b01001,
            0b01001,
            0b01110,
            0b00000
        ],
        "é": [
            0b00010,
            0b00100,
            0b01110,
            0b10001,
            0b11110,
            0b10000,
            0b01110,
            0b00000
        ],
        "è": [
            0b01000,
            0b00100,
            0b01110,
            0b10001,
            0b11110,
            0b10000,
            0b01110,
            0b00000
        ],
        "ẻ": [
            0b00100,
            0b00010,
            0b00100,
            0b01110,
            0b10001,
            0b11110,
            0b10000,
            0b01110
        ],
        "ẽ": [
            0b01101,
            0b10010,
            0b00100,
            0b01110,
            0b10001,
            0b11110,
            0b10000,
            0b01110
        ],
        "ẹ": [
            0b00000,
            0b00000,
            0b01110,
            0b10001,
            0b11110,
            0b10000,
            0b01110,
            0b00100
        ],
        "É": [
            0b00010,
            0b00100,
            0b11111,
            0b10000,
            0b11111,
            0b10000,
            0b11111,
            0b00000
        ],
        "È": [
            0b01000,
            0b00100,
            0b11111,
            0b10000,
            0b11111,
            0b10000,
            0b11111,
            0b00000
        ],
        "Ẻ": [
            0b00100,
            0b00010,
            0b00100,
            0b11111,
            0b10000,
            0b11111,
            0b10000,
            0b11111
        ],
        "Ẽ": [
            0b01101,
            0b10010,
            0b00000,
            0b11111,
            0b10000,
            0b11111,
            0b10000,
            0b11111
        ],
        "Ẹ": [
            0b11111,
            0b10000,
            0b10000,
            0b11111,
            0b10000,
            0b10000,
            0b11111,
            0b00100
        ],
        "í": [
            0b00010,
            0b00100,
            0b00000,
            0b00100,
            0b01100,
            0b00100,
            0b01110,
            0b00000
        ],
        "ì": [
            0b01000,
            0b00100,
            0b00000,
            0b00100,
            0b01100,
            0b00100,
            0b01110,
            0b00000
        ],
        "ỉ": [
            0b00100,
            0b00010,
            0b00100,
            0b00100,
            0b01100,
            0b00100,
            0b01110,
            0b00000
        ],
        "ĩ": [
            0b01101,
            0b10010,
            0b00000,
            0b00100,
            0b01100,
            0b00100,
            0b01110,
            0b00000
        ],
        "ị": [
            0b00000,
            0b00100,
            0b00000,
            0b00100,
            0b01100,
            0b00100,
            0b01110,
            0b00100
        ],
        "Í": [
            0b00010,
            0b00100,
            0b01110,
            0b00100,
            0b00100,
            0b00100,
            0b01110,
            0b00000
        ],
        "Ì": [
            0b01000,
            0b00100,
            0b01110,
            0b00100,
            0b00100,
            0b00100,
            0b01110,
            0b00000
        ],
        "Ỉ": [
            0b00100,
            0b00010,
            0b00100,
            0b01110,
            0b00100,
            0b00100,
            0b00100,
            0b01110
        ],
        "Ĩ": [
            0b01101,
            0b10010,
            0b00000,
            0b01110,
            0b00100,
            0b00100,
            0b00100,
            0b01110
        ],
        "Ị": [
            0b00000,
            0b00000,
            0b01110,
            0b00100,
            0b00100,
            0b00100,
            0b01110,
            0b00100
        ],
        "ó": [
            0b00010,
            0b00100,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000
        ],
        "ò": [
            0b01000,
            0b00100,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000
        ],
        "ỏ": [
            0b00100,
            0b00010,
            0b00100,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "õ": [
            0b01101,
            0b10010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000
        ],
        "ọ": [
            0b00000,
            0b00000,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00100
        ],
        "Ó": [
            0b00010,
            0b00100,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ò": [
            0b01000,
            0b00100,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ỏ": [
            0b00100,
            0b00010,
            0b00100,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Õ": [
            0b01101,
            0b10010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ọ": [
            0b00000,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00100
        ],
        "ô": [
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000
        ],
        "ố": [
            0b00010,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "ồ": [
            0b01000,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "ổ": [
            0b00100,
            0b00010,
            0b00100,
            0b11111,
            0b01110,
            0b10001,
            0b10001,
            0b01110
        ],
        "ỗ": [
            0b01101,
            0b10010,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b01110
        ],
        "ộ": [
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00100
        ],
        "Ô": [
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ố": [
            0b00010,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ồ": [
            0b01000,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ổ": [
            0b00100,
            0b00010,
            0b00100,
            0b11111,
            0b01110,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ỗ": [
            0b01101,
            0b10010,
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ộ": [
            0b01110,
            0b10001,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00100
        ],
        "ơ": [
            0b00000,
            0b00000,
            0b00001,
            0b01101,
            0b10010,
            0b10010,
            0b01100,
            0b00000
        ],
        "ớ": [
            0b00010,
            0b00100,
            0b00010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "ờ": [
            0b01000,
            0b00100,
            0b00010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "ở": [
            0b00100,
            0b00010,
            0b00110,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "ỡ": [
            0b01101,
            0b10010,
            0b00010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "ợ": [
            0b00000,
            0b00010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00100
        ],
        "Ơ": [
            0b00001,
            0b01101,
            0b10010,
            0b10010,
            0b10010,
            0b10010,
            0b01100,
            0b00000
        ],
        "Ớ": [
            0b00010,
            0b00100,
            0b00010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ờ": [
            0b01000,
            0b00100,
            0b00010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ở": [
            0b00100,
            0b00010,
            0b00110,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ỡ": [
            0b01101,
            0b10010,
            0b00010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ợ": [
            0b00000,
            0b00010,
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00100
        ],
        "ú": [
            0b00010,
            0b00100,
            0b10001,
            0b10001,
            0b10001,
            0b10011,
            0b01101,
            0b00000
        ],
        "ù": [
            0b01000,
            0b00100,
            0b10001,
            0b10001,
            0b10001,
            0b10011,
            0b01101,
            0b00000
        ],
        "ủ": [
            0b00100,
            0b00010,
            0b00100,
            0b10001,
            0b10001,
            0b10001,
            0b10011,
            0b01101
        ],
        "ũ": [
            0b01101,
            0b10010,
            0b00000,
            0b10001,
            0b10001,
            0b10001,
            0b10011,
            0b01101
        ],
        "ụ": [
            0b00000,
            0b00000,
            0b10001,
            0b10001,
            0b10001,
            0b10011,
            0b01101,
            0b00100
        ],
        "Ú": [
            0b00010,
            0b00100,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000
        ],
        "Ù": [
            0b01000,
            0b00100,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000
        ],
        "Ủ": [
            0b00100,
            0b00010,
            0b00100,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ũ": [
            0b01101,
            0b10010,
            0b00000,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ],
        "Ụ": [
            0b00000,
            0b00000,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00100
        ],
        "ư": [
            0b00000,
            0b00000,
            0b00001,
            0b10011,
            0b10010,
            0b10110,
            0b01010,
            0b00000
        ],
        "ứ": [
            0b00010,
            0b00100,
            0b00001,
            0b10011,
            0b10010,
            0b10110,
            0b01010,
            0b00000
        ],
        "ừ": [
            0b01000,
            0b00100,
            0b00001,
            0b10011,
            0b10010,
            0b10110,
            0b01010,
            0b00000
        ],
        "ử": [
            0b00100,
            0b00010,
            0b00100,
            0b00001,
            0b10011,
            0b10010,
            0b10110,
            0b01010
        ],
        "ữ": [
            0b01101,
            0b10010,
            0b00000,
            0b00001,
            0b10011,
            0b10010,
            0b10110,
            0b01010
        ],
        "ự": [
            0b00000,
            0b00000,
            0b00001,
            0b10011,
            0b10010,
            0b10110,
            0b01010,
            0b00100
        ],
        "Ứ": [
            0b00010,
            0b00101,
            0b10011,
            0b10010,
            0b10010,
            0b10010,
            0b01100,
            0b00000
        ],
        "Ừ": [
            0b01000,
            0b00101,
            0b10011,
            0b10010,
            0b10010,
            0b10010,
            0b01100,
            0b00000
        ],
        "Ử": [
            0b00100,
            0b00010,
            0b00101,
            0b10011,
            0b10010,
            0b10010,
            0b10010,
            0b01100
        ],
        "Ữ": [
            0b01101,
            0b10010,
            0b00001,
            0b10011,
            0b10010,
            0b10010,
            0b10010,
            0b01100
        ],
        "Ự": [
            0b00000,
            0b00001,
            0b10011,
            0b10010,
            0b10010,
            0b10010,
            0b01100,
            0b00100
        ],
        "ý": [
            0b00010,
            0b00100,
            0b10001,
            0b10001,
            0b01111,
            0b00001,
            0b01110,
            0b00000
        ],
        "ỳ": [
            0b01000,
            0b00100,
            0b10001,
            0b10001,
            0b01111,
            0b00001,
            0b01110,
            0b00000
        ],
        "ỷ": [
            0b00100,
            0b00010,
            0b10101,
            0b10001,
            0b01111,
            0b00001,
            0b01110,
            0b00000
        ],
        "ỹ": [
            0b01101,
            0b10010,
            0b00000,
            0b10001,
            0b10001,
            0b01111,
            0b00001,
            0b01110
        ],
        "ỵ": [
            0b00000,
            0b00000,
            0b10001,
            0b10001,
            0b01111,
            0b00001,
            0b01110,
            0b00100
        ],
        "Ý": [
            0b00010,
            0b10101,
            0b10001,
            0b10001,
            0b01010,
            0b00100,
            0b00100,
            0b00000
        ],
        "Ỳ": [
            0b01000,
            0b10101,
            0b10001,
            0b10001,
            0b01010,
            0b00100,
            0b00100,
            0b00000
        ],
        "Ỷ": [
            0b00100,
            0b00010,
            0b10101,
            0b10001,
            0b10001,
            0b01010,
            0b00100,
            0b00100
        ],
        "Ỹ": [
            0b01101,
            0b10010,
            0b10001,
            0b10001,
            0b10001,
            0b01010,
            0b00100,
            0b00100
        ],
        "Ỵ": [
            0b00000,
            0b10001,
            0b10001,
            0b10001,
            0b01010,
            0b00100,
            0b00100,
            0b00100
        ]
    }