# Drivers for MicroPython on the Octopus Lab Robot Board

Note: This is still a draft.


## Uploading

The drivers can be uploaded at once using:

    ampy -p /dev/ttyUSB0 put drivers

where `/dev/ttyUSB0` is the port to the device.

The `devices.py` file includes some configuration (for a fully populated board).

Demos can be run with:

```python
import devices

devices.board.demo()
devices.stepper1.demo()
devices.stepper2.demo()
devices.motor1.demo()
devices.motor2.demo()
devices.servo1.demo()
devices.servo2.demo()
devices.servo3.demo()
```

If you upload `devices.py` as `boot.py`, you'll be able to tab-complete devices
such as `servo1` or `motor2` directly!


## Design notes

Device constructors take either `Pin` or `int`. A Pin objects are created
automatically if an int is passed in.

Preferably, values are set/read by *calling* the `Pin`.
This allows an arbitrary callable to be passed instead of the Pin.

As in core MicroPython, values are set and read by calling the same method,
with zero arguments (for reading) or one argument (for writing).

Devices have a `demo` method, which serves as a quick functionality check.
(And it's tab-completable!)

The `devices.py` file depends on how the board is wired/connected, so users
are expected to change it.
The `drivers` are not expected to change very frequently.
