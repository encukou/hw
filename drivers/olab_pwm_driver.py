"""
Driver for the PCA9685 16-channel I2C PWM driver

Copyright (c) 2018 Petr Viktorin

Based on the Adafruit PCA9685 driver:
    https://github.com/adafruit/micropython-adafruit-pca9685
    Copyright (c) 2016 Radomir Dopieralski, written for Adafruit Industries

Licensed under the MIT License


After initialization, this class can be indexed to get individual PWM objects.
For example, for a SG90 servo connected to the first output:

    pca = PCA9685(i2c, 0x40, freq=50)
    servo = olab_servo.SG90(pwm=pca[0])

Note that the frequency is shared and cannot be set on the individual PWMs.
"""

import ustruct
import time

MODE1 = const(0x00)
MODE2 = const(0x01)
SUBADDR1 = const(0x02)
SUBADDR2 = const(0x03)
SUBADDR3 = const(0x04)
ALLCALLADDR = const(0x05)
ONOFF = const(0x06)
PRE_SCALE = const(0xfe)
TEST_MODE = const(0xff)

MODE1_ALLCALL = const(0x01)
MODE1_SUB3 = const(0x02)
MODE1_SUB2 = const(0x04)
MODE1_SUB1 = const(0x08)
MODE1_SLEEP = const(0x10)
MODE1_AI = const(0x20)
MODE1_EXTCLK = const(0x40)
MODE1_RESTART = const(0x80)

MODE2_OUTNE0 = const(0x01)
MODE2_OUTNE1 = const(0x02)
MODE2_OUTDRV = const(0x04)
MODE2_OCH = const(0x08)
MODE2_INVRT = const(0x10)

ONOFF_ALWAYS = const(0x1000)

MAX_DUTY = const(0x1000)

OSCILLATOR_FREQ = 25000000


class PCA9685:
    max_duty = MAX_DUTY

    def __init__(self, i2c, address=0x40, freq=None):
        self.i2c = i2c
        self.address = address
        self.reset()
        if freq:
            self.freq(freq)

    def _write(self, address, value):
        self.i2c.writeto_mem(self.address, address, bytearray([value]))

    def _read(self, address):
        return self.i2c.readfrom_mem(self.address, address, 1)[0]

    def reset(self):
        self._write(MODE1, MODE1_AI)

    def freq(self, freq=None):
        """Set or read the frequency in Hz"""
        if freq is None:
            return int(OSCILLATOR_FREQ / MAX_DUTY / (self._read(PRE_SCALE) - 0.5))
        prescale = int(OSCILLATOR_FREQ / MAX_DUTY / freq + 0.5)
        old_mode = self._read(MODE1)
        self._write(MODE1, (old_mode & ~MODE1_SLEEP) | MODE1_SLEEP)
        self._write(PRE_SCALE, prescale)
        self._write(MODE1, old_mode)
        time.sleep_us(5)
        self._write(MODE1, old_mode | MODE1_RESTART | MODE1_AI)

    def pwm(self, index, on=None, off=None):
        """Set the on & off time (12-bit values + 1 always-on/off bit)"""
        if on is None or off is None:
            data = self.i2c.readfrom_mem(self.address, ONOFF + 4 * index, 4)
            return ustruct.unpack('<HH', data)
        data = ustruct.pack('<HH', on, off)
        self.i2c.writeto_mem(self.address, ONOFF + 4 * index,  data)

    def duty(self, index, value=None):
        if value is None:
            on, off = self.pwm(index)
            if off & ONOFF_ALWAYS:
                return 0
            if on & ONOFF_ALWAYS:
                return MAX_DUTY
            value = on - off
            if value < 0:
                value += MAX_DUTY
            return value
        if not 0 <= value <= MAX_DUTY:
            raise ValueError("duty out of range")
        if value == 0:
            self.pwm(index, 0, ONOFF_ALWAYS)
        elif value == MAX_DUTY:
            self.pwm(index, ONOFF_ALWAYS, 0)
        else:
            self.pwm(index, 0, value)

    def duty_fraction(self, index, value=None):
        if value is None:
            return self.duty(index) / MAX_DUTY
        else:
            self.duty(index, int(value * MAX_DUTY))

    def __getitem__(self, index):
        return PWMChannel(self, index)


class PWMChannel:
    max_duty = MAX_DUTY

    def __init__(self, controller, index):
        self.controller = controller
        self.index = index

    def freq(self, value=None):
        if value is None:
            return self.controller.freq()
        else:
            raise TypeError(
                'PCA9685 frequency cannot be controlled per channel'
            )

    def duty(self, value=None):
        return self.controller.duty(self.index, value)

    def duty_fraction(self, index, value=None):
        return self.controller.duty_fraction(self.index, value)
