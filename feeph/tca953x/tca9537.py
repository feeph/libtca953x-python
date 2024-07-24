#!/usr/bin/env python3
"""
TCA9537 - 4-Bit I²C I/O Expander with Configuration Registers

datasheet: # https://www.ti.com/lit/ds/symlink/tca9537.pdf
"""

import logging

# module busio provides no type hints
import busio  # type: ignore
from feeph.i2c import BurstHandler

from feeph.tca953x.shared import PinMode, PinPolarity

LH = logging.getLogger('tca953x')


DEFAULTS = {
    #     value           purpose                             section
    # -----------------------------------------------------------------
    0x00: 0b1111_0000,  # input port (ro)                     8.6.3
    0x01: 0b1111_1111,  # output port (rw)                    8.6.3
    0x02: 0b0000_0000,  # polarity inversion (rw)             8.6.3
    0x03: 0b1111_1111,  # configuration (rw)                  8.6.3
}


class TCA9537:
    """
    <just an example - replace with some actual code>
    """

    def __init__(self, i2c_bus: busio.I2C):
        """
        initialize the object

        Configure pin 6 and the control mode before use.
        These settings MUST match the electric circuit!
         - emc2101.configure_pin_six_as_alert()
         - emc2101.configure_pin_six_as_tacho()
         - emc2101.configure_dac_control()
         - emc2101.configure_pwm_control()

        If you don't set these values correctly you won't get sensible
        readings!
        """
        self._i2c_bus = i2c_bus
        self._i2c_adr = 0x49  # the I²C bus address is hardcoded

    def reset_device_registers(self):
        with BurstHandler(i2c_bus=self._i2c_bus, i2c_adr=self._i2c_adr) as bh:
            for register, value in DEFAULTS.items():
                bh.write_register(register=register, value=value)

    def get_pin_modes(self) -> tuple[PinMode, PinMode, PinMode, PinMode]:
        pin0 = pin1 = pin2 = pin3 = PinMode.OUTPUT
        with BurstHandler(i2c_bus=self._i2c_bus, i2c_adr=self._i2c_adr) as bh:
            pin_cfg = bh.read_register(0x03)
        if pin_cfg & 0b0000_0001:
            pin0 = PinMode.INPUT
        if pin_cfg & 0b0000_0010:
            pin1 = PinMode.INPUT
        if pin_cfg & 0b0000_0100:
            pin2 = PinMode.INPUT
        if pin_cfg & 0b0000_1000:
            pin3 = PinMode.INPUT
        return (pin0, pin1, pin2, pin3)

    def set_pin_modes(self, pin0: PinMode, pin1: PinMode, pin2: PinMode, pin3: PinMode):
        pin_cfg = 0b0000_0000
        if pin0 == PinMode.INPUT:
            pin_cfg |= 0b0000_0001
        if pin1 == PinMode.INPUT:
            pin_cfg |= 0b0000_0010
        if pin2 == PinMode.INPUT:
            pin_cfg |= 0b0000_0100
        if pin3 == PinMode.INPUT:
            pin_cfg |= 0b0000_1000
        with BurstHandler(i2c_bus=self._i2c_bus, i2c_adr=self._i2c_adr) as bh:
            return bh.write_register(0x03, pin_cfg)

    def get_pin_polarity(self) -> tuple[PinPolarity, PinPolarity, PinPolarity, PinPolarity]:
        pin0 = pin1 = pin2 = pin3 = PinPolarity.MATCHING
        with BurstHandler(i2c_bus=self._i2c_bus, i2c_adr=self._i2c_adr) as bh:
            pin_cfg = bh.read_register(0x02)
        if pin_cfg & 0b0000_0001:
            pin0 = PinPolarity.INVERTED
        if pin_cfg & 0b0000_0010:
            pin1 = PinPolarity.INVERTED
        if pin_cfg & 0b0000_0100:
            pin2 = PinPolarity.INVERTED
        if pin_cfg & 0b0000_1000:
            pin3 = PinPolarity.INVERTED
        return (pin0, pin1, pin2, pin3)

    def set_pin_polarity(self, pin0: PinPolarity, pin1: PinPolarity, pin2: PinPolarity, pin3: PinPolarity):
        pin_cfg = 0b0000_0000
        if pin0 == PinPolarity.INVERTED:
            pin_cfg |= 0b0000_0001
        if pin1 == PinPolarity.INVERTED:
            pin_cfg |= 0b0000_0010
        if pin2 == PinPolarity.INVERTED:
            pin_cfg |= 0b0000_0100
        if pin3 == PinPolarity.INVERTED:
            pin_cfg |= 0b0000_1000
        with BurstHandler(i2c_bus=self._i2c_bus, i2c_adr=self._i2c_adr) as bh:
            return bh.write_register(0x02, pin_cfg)

    def get_pin_state(self, pin: int) -> bool:
        if not 0 <= pin <= 3:
            raise ValueError("pin number exceeds allowed range (0 ≤ x ≤ 3)")
        with BurstHandler(i2c_bus=self._i2c_bus, i2c_adr=self._i2c_adr) as bh:
            pin_bit = 1 << pin  # used for mode and state, e.g. 0b0000_0010
            pin_cfg = bh.read_register(0x03)
            if pin_cfg & pin_bit:
                # read state of input pin from input register
                return bool(bh.read_register(0x00) & pin_bit)
            else:
                # read state of output pin from output register
                return bool(bh.read_register(0x01) & pin_bit)

    def set_pin_state(self, pin: int, is_active: bool) -> bool:
        if not 0 <= pin <= 3:
            raise ValueError("pin number exceeds allowed range (0 ≤ x ≤ 3)")
        with BurstHandler(i2c_bus=self._i2c_bus, i2c_adr=self._i2c_adr) as bh:
            pin_bit = 1 << pin  # used for mode and state, e.g. 0b0000_0010
            pin_cfg = bh.read_register(0x03)
            if pin_cfg & pin_bit:
                # refuse to modify an input pin
                return False
            else:
                cur_pin_states = bh.read_register(0x01)
                if is_active:
                    # enable the pin's bit
                    new_pin_states = cur_pin_states | pin_bit
                else:
                    # disable the pin's bit
                    new_pin_states = cur_pin_states & ~(pin_bit)
                bh.write_register(0x01, new_pin_states)
                return True

    # The Input Port register reflects the incoming logic levels of the
    # pins, regardless of whether the pin is defined as an input or an
    # output by the configuration register.

    # The Output Port register shows the outgoing logic levels of the pins
    # defined as outputs by the Configuration register. Bit values in this
    # register have no effect on pins defined as inputs. In turn, reads
    # from this register reflect the value that is in the flip-flop
    # controlling the output selection, not the actual pin value.
