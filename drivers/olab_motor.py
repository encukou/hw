"""
A L293D motor driver

L293DMotor drives a DC motor connected to one H-bridge of the L293D chip.

The motor's speed can be controlled via the speed() method, with a float range
from -1 to 1 (negative values being the opposite direction).

Alternatively, the `duty()` method takes an int in the range -1023 to 1023,
and sets the speed directly. (The name `duty` is a bit incorrect, as it
encodes the direction as well as the PWM duty cycle.)

Both `speed()` and `duty()` return the current value when called without
arguments, and set it when called with an argument.

Motors are driven using PWM on the ENable pin. The pulse width will probably
not have a linear correlation to the actual speed.
(Speeds lower than about 0.3 might not even turn the motor on.)

To deinitialize the motor driver, and free the PWM timer, call deinit().
"""

import machine

def _to_pin(pin):
    if isinstance(pin, int):
        return machine.Pin(pin, machine.Pin.OUT)
    return pin

class L293DMotor:
    def __init__(self, enable_pin, pin_a, pin_b, freq=100):
        self._en = _to_pin(enable_pin)
        self._a = _to_pin(pin_a)
        self._b = _to_pin(pin_b)
        self._direction = 0
        self._pwm = None
        self._freq = 100

    def deinit(self):
        """Turn the motor off and free resources"""
        if self._pwm:
            self._pwm.deinit()
        self._pwm = None
        self._en(0)
        self._a(0)
        self._b(0)

    def duty(self, duty=None):
        if duty is None:
            if self._pwm is None:
                return 0
            return self._pwm.duty() * (self._b() - self._a())
        if self._pwm is None:
            self._pwm = machine.PWM(self._en, freq=self._freq, duty=abs(duty))
        else:
            self._pwm.duty(abs(duty))
        self._a(duty < 0)
        self._b(duty > 0)

    def speed(self, speed=None):
        if speed is None:
            return self.duty() / 1023
        else:
            self.duty(int(speed * 1023))

    def on(self, speed=1):
        self.speed(speed)

    def off(self):
        """Turn the motor off (temporarily)

        If the motor won't be used for a while, consider using deinit()
        instead.
        """
        self.speed(0)

    def __repr__(self):
        if self._pwm:
            return '<L293DMotor {:+}>'.format(self.speed())
        else:
            return '<L293DMotor off>'

    def demo(self):
        """Turn the motor back and forth with increasing speed"""
        from time import sleep
        direction = 1
        for i in range(3, 10):
            self.speed(i / 10 * direction)
            direction *= -1
            sleep(1 / 5)
        self.deinit()
