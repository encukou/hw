"""
Driver for the SG90 PWM-controlled servo

Use the `value()` method to turn the servo to a given value.

Use `release()` to power the motor off.

By default, the servo is positioned in degrees, -90 to +90.
To use different units, set "min_value" and "max_value" to the min/max
values you wish to use.

Calibrate the servo by setting min_pulse_ms and max_pulse_ms.
The datasheet says pulse width should be 1ms to 2ms.
"""

import machine

class SG90:
    def __init__(
        self, pin,
        min_value=-90, max_value=90,
        min_pulse_ms=1, max_pulse_ms=2,
        freq=50,
    ):
        if isinstance(pin, int):
            pin = machine.Pin(pin, machine.Pin.OUT)
        self._min_value = min_value
        self._max_value = max_value
        self._value_range = max_value - min_value
        period_ms = 1000 / freq
        self._min_duty = min_pulse_ms / period_ms * 1024
        self._max_duty = max_pulse_ms / period_ms * 1024
        if not (0 < self._min_duty < self._max_duty < 1024):
            raise ValueError('pulse width or freq out of range')
        self._duty_range = self._max_duty - self._min_duty
        self._pwm = machine.PWM(pin, freq=freq, duty=0)

    def value(self, value=None):
        if value is None:
            duty = self._pwm.duty()
            if duty == 0:
                return None
            else:
                duty = self._pwm.duty()
                normalized = (duty - self._min_duty) / self._duty_range
                return normalized * self._value_range + self._min_value
        else:
            normalized = (value - self._min_value) / self._value_range
            duty = int(normalized * self._duty_range + self._min_duty)
            self._pwm.duty(duty)

    __call__ = value

    def release(self):
        self._pwm.duty(0)

    def __repr__(self):
        if self._pwm.duty() == 0:
            duty_repr = 'off'
        else:
            duty_repr = self.value()
        return '<Servo @ {}>'.format(duty_repr)

    def demo(self):
        from time import sleep
        self.value(self._max_value)
        sleep(0.5)
        self.value(self._min_value)
        sleep(0.5)
        self.release()
