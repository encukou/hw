"""
Driver for the PCF8574 I2C I/O expander

Controlling individual pins:
    # Read pin #2
    print(expander.read(2))

    # Toggle pin #2
    expander.toggle(2)

    # Write pin #6
    expander.write(6, 1)

Controlling several pins, using a bit mask:
    expander.read_bits(mask=0xf)

    expander.write_bits(0xf0, mask=0xf0)

Controlling groups of pins individually:
    # Read the first four bits (0-3)
    first_half = expander[0:4]
    print(first_half.value())

    # Write bits 4-7
    last_half = expander[4:]
    last_half.value(0b0101)
"""

class PCF8574:
    def __init__(self, i2c, address):
        self._i2c = i2c
        self._address = address
        self._input = 0xff  # Pins are HIGH after power-on
        self._input_mask = 0xff  # Mask specifying which pins are used as input
        self._output = 0

    def _read(self):
        # NB: input pins must be written as HIGH before reading!
        in_bytes = self._i2c.readfrom(self._address, 1)
        self._input = in_bytes[0] & self._input_mask

    def _write(self):
        self._i2c.writeto(self._address, bytes([self._output | self._input_mask]))

    def write_bits(self, value, mask=0xff):
        """Write value to several pins, specified by mask.

        Pins identified by pin_mask are set to output mode.
        """
        self._input_mask &= ~mask
        self._output = (self._output & ~mask) | (value & mask)
        self._write()

    def read_bits(self, mask=0xff):
        """Read value on several pins, specified by mask.

        Pins identified by pin_mask are set to input mode, and connected to
        weak pull-ups.
        """
        self._input_mask &= mask
        if (self._output & self._input_mask) != self._input_mask:
            # Set inputs HIGH before reading
            self._output |= self._input_mask
            self._write()
        self._read()
        return self._input & mask

    def write(self, pin, value):
        """Write value to a single pin. The pin is set to output mode."""
        self.write_bits((value & 1) << pin, mask=1 << pin)

    def read(self, pin):
        """Read value from a single pin. The pin is set to input mode."""
        return self.read_bits(mask=1 << pin) >> pin

    def toggle(self, pin):
        """Toggle value of a single pin. The pin should be in output mode."""
        value = self._output ^ (1 << pin)
        mask = 1 << pin
        self.write_bits(value, mask)

    def value(self, new_value=None):
        """Read or set all pins

        If value is None, read all pins. All are set to input mode.
        Otherwise, write all pins according to the value. All pins are
        set to output mode.
        """
        if new_value is None:
            return self.expander.read_bits()
        else:
            self.expander.write_bits(new_value)

    def __getitem__(self, item):
        """Get a subset of pins, on which value() can be called.

        Individual pins or a range can be specified

        Example: Read pin 6
            pin6 = expander[6]
            print(pin6.value())

        Example - set first 4 bits:
            first_half = expander[:4]
            first_half.value(0xf)

        As with `machine.Pin`, the result is callable directly, with the same
        effect as calling `value()`.
        """
        if isinstance(item, slice):
            if item.step is not None and item.step != 1:
                raise ValueError('Slice step not implemented')
            start = item.start
            stop = item.stop
            if start is None:
                start = 0
            if stop is None:
                stop = 8
            shift = start
            mask = (0xff >> (start+8-stop))
            return _ExpanderBitSubset(self, mask, shift)
        elif isinstance(item, int):
            return _ExpanderBitSubset(self, 1, item)
        else:
            raise TypeError(type(item).__name__)

    def __repr__(self):
        pin_repr = _pin_repr(self._input, self._output, self._input_mask, 0xff)
        return '<PCF8574{}>'.format(pin_repr)


def _pin_repr(input, output, input_mask, mask):
    in_descriptions = []
    out_descriptions = []
    in_format = ''
    out_format = ''
    for pin in range(8):
        if not ((1 << pin) & mask):
            continue
        if (input_mask >> pin) & 1:
            out_descriptions.append('_')
            in_descriptions.append(str((input >> pin) & 1))
            in_format = ', last in:{}'
        else:
            in_descriptions.append('_')
            out_descriptions.append(str((output >> pin) & 1))
            out_format = ', out:{}'
    in_desc = in_format.format(''.join(reversed(in_descriptions)))
    out_desc = out_format.format(''.join(reversed(out_descriptions)))
    return in_desc + out_desc


class _ExpanderBitSubset:
    def __init__(self, expander, mask, shift):
        self.expander = expander
        self._mask = mask
        self._shift = shift

    def value(self, new_value=None):
        shift = self._shift
        if new_value is None:
            return self.expander.read_bits(self._mask << shift) >> shift
        else:
            self.expander.write_bits(new_value << shift, self._mask << shift)

    __call__ = value

    def __repr__(self):
        ones = bin(self._mask).count('1')
        if ones == 1:
            stop_repr = ''
        else:
            stop_repr = ':' + str(self._shift + ones)
        exp = self.expander
        pin_repr = _pin_repr(
            exp._input, exp._output, exp._input_mask, self._mask,
        )
        return '<PCF8574[{}{}]{}>'.format(self._shift, stop_repr, pin_repr)
