"""
Pinout for the OctopusLab robotBoard PCB and esp32 soc
Edition: --- 2.12.2018 ---

For version 1 of the board, pass `version=1` to the constructor.


Example usage:

from olab_esp32_robot_board input RobotBoard
board = RobotBoard()

board.demo()

# Get an output pin (as machine.Pin):
board.pin_out(board.PWM1)
board.pin_out('PWM1')

# Get an input pin:
board.pin_in(board.ONE_WIRE)
board.pin_in('ONE_WIRE')
"""

from micropython import const
import machine


class RobotBoard:
    # PINs on the ESP32 board
    BUILT_IN_LED = 2
    HALL_SENSOR = 8

    # I2C
    I2C_SCL = 22
    I2C_SDA = 21

    # SPI
    SPI_CLK = 18
    SPI_MISO = 19
    SPI_MOSI = 23
    SPI_CS0 = 5

    # WS2812 LED & DEVn pins
    WSLED = 15     # Robot Board v2
    DEV1 = 32
    DEV2 = 33

    # One Wire protocol (e.g. for Dallas temperature sensor)
    ONE_WIRE = 32

    # DC motors (via L293D dual H-bridge)
    MOTOR_12EN = 25
    ##MOTOR_34EN = 15 # Robot Board v1
    MOTOR_34EN = 13   # Robot Board v2
    MOTOR_1A = 26
    MOTOR_2A = 12
    MOTOR_3A = 14
    MOTOR_4A = 27

    # Main analog input (used for LiPo power management)
    ANALOG_IN = 36

    # PWM/servos
    PWM1 = 17
    PWM2 = 16
    PWM3 = 4

    # Inputs
    I39 = 39
    I34 = 34
    I35 = 35

    _i2c = None

    def __init__(self, version=2):
        self.version = version
        if version <= 1:
            # Update pins for the older version
            self.WSLED = 13
            self.MOTOR_34EN = 15

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

    def get_i2c(self):
        if self._i2c is None:
            Pin = machine.Pin
            self._i2c = machine.I2C(
                scl=Pin(self.I2C_SCL, Pin.OUT, Pin.PULL_UP),
                sda=Pin(self.I2C_SDA, Pin.OUT, Pin.PULL_UP),
            )
        return self._i2c

    def demo(self):
        """Fade the on-board LED in and out"""
        from time import sleep_ms
        pwm = machine.PWM(self.pin_out(self.BUILT_IN_LED), freq=100, duty=0)
        SPEED = 4
        for duty in range(0, 1024, SPEED):
            pwm.duty(duty)
            sleep_ms(1)
        for duty in range(1024, 0, -SPEED):
            pwm.duty(duty)
            sleep_ms(1)
        pwm.deinit()
