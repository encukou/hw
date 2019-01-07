"""
Pinout for the NodeMCU v2
"""

from micropython import const
import machine


class NodeMCU:
    # PINs on the NodeMCU v2 board
    D0 = 16
    D1 = 5
    D2 = 4
    D3 = 0
    D4 = 2
    D5 = 14
    D6 = 12
    D7 = 13
    D8 = 15

    RX = 3
    TX = 1

    BUILT_IN_LED_INV = 2  # NodeMCU on the ESP8266 uses inverted logic
    FLASH = 0

    def pin_number(self, name):
        if isinstance(name, int):
            return name
        else:
            number = getattr(self, name)
            if not isinstance(number, int):
                raise KeyError(name)
            return number

    def pin_out(self, name):
        number = self.pin_number(name)
        Pin = machine.Pin
        return Pin(number, Pin.OUT)

    def pin_in(self, name):
        number = self.pin_number(name)
        Pin = machine.Pin
        return Pin(number, Pin.IN, Pin.PULL_UP)

    def demo(self):
        """Fade the on-board LED in and out"""
        from time import sleep_ms
        pin = self.pin_out(self.BUILT_IN_LED_INV)
        pwm = machine.PWM(pin, freq=100, duty=0)
        SPEED = 4
        for duty in range(1024, 0, -SPEED):
            pwm.duty(duty)
            sleep_ms(1)
        for duty in range(0, 1024, SPEED):
            pwm.duty(duty)
            sleep_ms(1)
        pwm.deinit()
        pin(1)
