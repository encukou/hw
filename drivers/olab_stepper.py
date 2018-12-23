"""
MicroPython 28BYJ-48 step motor on ULN2803 driver via PFC8574 I2C expander
"""
# Based on octopus LAB library:
# https://raw.githubusercontent.com/octopusengine/octopuslab/master/esp32-micropython/lib/sm28byj48.py

import time
from micropython import const

STEP_ELEMENTS = (
    const(0b0001),
    const(0b0011),
    const(0b0010),
    const(0b0110),
    const(0b0100),
    const(0b1100),
    const(0b1000),
    const(0b1001)
)
N_STEP_ELEMENTS = const(8)


class SM28BYJ48:
    def __init__(self, set_bits):
        """
        set_bits should be a callable, which is called with a 4-bit integer
        to set the motor's position.

        With an IO expander using the olab_io_expander driver,
        you can use use `expander[0:4]` or `expander[4:8]`.
        """
        self.set_bits = set_bits
        self.current_step = 0

    def turn_steps(self, steps, delay_ms=1):
        """Turn the given amount of steps (positive = clockwise)

        There are 8 steps per turn.
        The delay per step must be at least 1ms for the motor to turn.
        """
        if steps < 0:
            direction = -1
        else:
            direction = 1
        for _ in range(abs(int(steps))):
            self.current_step += direction
            element = STEP_ELEMENTS[self.current_step % N_STEP_ELEMENTS ]
            self.set_bits(element)
            time.sleep_ms(delay_ms)

    def turn_degree(self, angle, ccw=False):
        # 64 / 45 is a gearbox included in 28BYJ-48 step motor
        step_count = angle * 8 * 64 / 45
        self.turn_steps(step_count)

    def demo(self):
        self.turn_degree(90)
        self.turn_degree(-90)
