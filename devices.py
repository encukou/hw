import machine

from drivers.olab_esp32_robot_board import RobotBoard

from drivers.olab_io_expander import PCF8574
from drivers.olab_stepper import SM28BYJ48
from drivers.olab_motor import L293DMotor
from drivers.olab_servo import SG90
#from drivers.olab_temperature import DS18B20
#from drivers.olab_display import SSH1106
#from drivers.olab_led import LED
#from drivers.olab_ledstrip import WS2812

board = RobotBoard(version=1)

i2c = board.get_i2c()
expander = PCF8574(i2c, address=0x23)

stepper1 = SM28BYJ48(expander[:4])
stepper2 = SM28BYJ48(expander[:4])

motor1 = L293DMotor(board.MOTOR_12EN, board.MOTOR_1A, board.MOTOR_2A)
motor2 = L293DMotor(board.MOTOR_34EN, board.MOTOR_3A, board.MOTOR_4A)

servo1 = SG90(board.PWM1)
servo2 = SG90(board.PWM2)
servo3 = SG90(board.PWM3)
