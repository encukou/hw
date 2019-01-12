"""
Driver for the SG90 PWM-controlled servo

Can be initialized in several ways:
- By passing `pin` -- a pin object (machine.Pin) or its address (int).
  A PWM object will be created automatically.
  Optionally, its frequency can be controlled by passing `freq`.
- By passing `pwm` -- a PWM object with `duty` and `freq` methods.
  If `freq` is given, that frequency will be set using `pwm.freq`.
  Otherwise, the frequency will be determined from the PWM object.
  If `max_duty` is given, it will be used as the value representing 100%
  duty cycle.
  Otherwise, it is read from `pwm.max_duty`, falling back to 1024.

Use the `value()` method to turn the servo to a given value.

Use `release()` to power the motor off.

By default, the servo is positioned in degrees, -90 to +90.
To use different units, set "min_value" and "max_value" to the min/max
values you wish to use.

Calibrate the servo by setting min_pulse_ms and max_pulse_ms.
"""

import machine

class SG90:
    def __init__(
        self, pin=None,
        *,
        pwm=None, freq=None, max_duty=None,
        min_value=-90, max_value=90,
        min_pulse_ms=0.5, max_pulse_ms=2.5,
    ):
        if pin is not None:
            if pwm is not None:
                raise ValueError('pin, pwm are mutually exclusive')
            if isinstance(pwm, int):
                pwm = machine.Pin(pwm, machine.Pin.OUT)
            freq = freq or 50
            self._pwm = machine.PWM(pin, freq=freq, duty=0)
            max_duty = max_duty or 1024
        elif pwm is not None:
            self._pwm = pwm
            if freq:
                pwm.freq(freq)
            else:
                freq = pwm.freq()
            max_duty = getattr(pwm, 'max_duty', 1024)
        else:
            raise ValueError('one of pin or pwm must be specified')

        self._min_value = min_value
        self._max_value = max_value
        self._value_range = max_value - min_value
        period_ms = 1000 / freq
        self._min_duty = min_pulse_ms / period_ms * max_duty
        self._max_duty = max_pulse_ms / period_ms * max_duty
        if not (0 < self._min_duty < self._max_duty < max_duty):
            raise ValueError('pulse width or freq out of range')
        self._duty_range = self._max_duty - self._min_duty

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
