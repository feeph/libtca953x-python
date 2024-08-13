#!/usr/bin/env python3
"""
"""

import unittest

from feeph.i2c import BurstHandler, EmulatedI2C

import feeph.tca953x as sut
import feeph.tca953x.tca9537


# pylint: disable=protected-access
class TestTCA9537(unittest.TestCase):

    def setUp(self):
        # initialize read/write registers
        registers = feeph.tca953x.tca9537.DEFAULTS.copy()
        self.i2c_adr = 0x49
        self.i2c_bus = EmulatedI2C(state={self.i2c_adr: registers})
        self.tca9537 = sut.TCA9537(i2c_bus=self.i2c_bus)
        # restore original state after each run
        # (hardware is not stateless)
        self.tca9537.reset_device_registers()

    def tearDown(self):
        # nothing to do
        pass

    # ---------------------------------------------------------------------

    def test_get_mode(self):
        self.i2c_bus._state[self.i2c_adr][0x03] = 0b0000_0110
        # -----------------------------------------------------------------
        computed = self.tca9537.get_pin_modes()
        expected = (sut.PinMode.OUTPUT, sut.PinMode.INPUT, sut.PinMode.INPUT, sut.PinMode.OUTPUT)
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_get_mode_inverted(self):
        # basically the same as test_get_mode(); this test is provided to
        # ensure we exercise all branch conditions in get_pin_modes()
        self.i2c_bus._state[self.i2c_adr][0x03] = 0b0000_1001
        # -----------------------------------------------------------------
        computed = self.tca9537.get_pin_modes()
        expected = (sut.PinMode.INPUT, sut.PinMode.OUTPUT, sut.PinMode.OUTPUT, sut.PinMode.INPUT)
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_set_mode_all_inputs(self):
        self.tca9537.set_pin_modes(sut.PinMode.INPUT, sut.PinMode.INPUT, sut.PinMode.INPUT, sut.PinMode.INPUT)
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            computed = bh.read_register(0x03)
        expected = 0b0000_1111
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_set_mode_all_outputs(self):
        self.tca9537.set_pin_modes(sut.PinMode.OUTPUT, sut.PinMode.OUTPUT, sut.PinMode.OUTPUT, sut.PinMode.OUTPUT)
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            computed = bh.read_register(0x03)
        expected = 0b0000_0000
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_set_mode_mixed(self):
        self.tca9537.set_pin_modes(sut.PinMode.OUTPUT, sut.PinMode.INPUT, sut.PinMode.OUTPUT, sut.PinMode.OUTPUT)
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            computed = bh.read_register(0x03)
        expected = 0b0000_0010
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    # ---------------------------------------------------------------------

    def test_get_polarity(self):
        self.i2c_bus._state[self.i2c_adr][0x02] = 0b0000_0110
        # -----------------------------------------------------------------
        computed = self.tca9537.get_pin_polarity()
        expected = (sut.PinPolarity.MATCHING, sut.PinPolarity.INVERTED, sut.PinPolarity.INVERTED, sut.PinPolarity.MATCHING)
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_get_polarity_inverted(self):
        # basically the same as test_get_polarity(); this test is provided to
        # ensure we exercise all branch conditions in get_pin_polarity()
        self.i2c_bus._state[self.i2c_adr][0x02] = 0b0000_1001
        # -----------------------------------------------------------------
        computed = self.tca9537.get_pin_polarity()
        expected = (sut.PinPolarity.INVERTED, sut.PinPolarity.MATCHING, sut.PinPolarity.MATCHING, sut.PinPolarity.INVERTED)
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_set_polarity_all_matching(self):
        self.tca9537.set_pin_polarity(sut.PinPolarity.MATCHING, sut.PinPolarity.MATCHING, sut.PinPolarity.MATCHING, sut.PinPolarity.MATCHING)
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            computed = bh.read_register(0x02)
        expected = 0b0000_0000
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_set_polarity_all_inverted(self):
        self.tca9537.set_pin_polarity(sut.PinPolarity.INVERTED, sut.PinPolarity.INVERTED, sut.PinPolarity.INVERTED, sut.PinPolarity.INVERTED)
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            computed = bh.read_register(0x02)
        expected = 0b0000_1111
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_set_polarity_as_mixed(self):
        self.tca9537.set_pin_polarity(sut.PinPolarity.MATCHING, sut.PinPolarity.INVERTED, sut.PinPolarity.MATCHING, sut.PinPolarity.MATCHING)
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            computed = bh.read_register(0x02)
        expected = 0b0000_0010
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    # ---------------------------------------------------------------------

    def test_get_input_pin_state(self):
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            bh.write_register(0x00, 0b0000_0100)  # pin 2 has a signal
            bh.write_register(0x01, 0b0000_0000)
            bh.write_register(0x03, 0b0000_0100)  # pin 2 is an input
        # -----------------------------------------------------------------
        computed = self.tca9537.get_pin_state(pin=2)
        expected = True
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_get_invalid_pin(self):
        self.assertRaises(ValueError, self.tca9537.get_pin_state, pin=4)

    def test_set_input_pin_state(self):
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            bh.write_register(0x01, 0b0000_1011)
        # ignore request, pin0 is configured as an input pin
        computed = self.tca9537.set_pin_state(pin=0, is_active=True)
        expected = False
        self.assertEqual(computed, expected)

    def test_get_output_pin_state(self):
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            bh.write_register(0x00, 0b0000_0000)
            bh.write_register(0x01, 0b0000_0100)  # pin 2 is active
            bh.write_register(0x03, 0b0000_0000)  # pin 2 is an output
        # -----------------------------------------------------------------
        computed = self.tca9537.get_pin_state(pin=2)
        expected = True
        # -----------------------------------------------------------------
        self.assertEqual(computed, expected)

    def test_set_output_pin_to_active(self):
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            # disable all outputs
            bh.write_register(0x01, 0b0000_0000)
        self.tca9537.set_pin_modes(sut.PinMode.INPUT, sut.PinMode.OUTPUT, sut.PinMode.INPUT, sut.PinMode.INPUT)
        # -----------------------------------------------------------------
        # honor request, pin 1 is configured as an output pin
        computed = self.tca9537.set_pin_state(pin=1, is_active=True)
        expected = True
        self.assertEqual(computed, expected)
        # -----------------------------------------------------------------
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            self.assertEqual(bh.read_register(0x01), 0b0000_0010)

    def test_set_output_pin_to_inactive(self):
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            # enable all outputs
            bh.write_register(0x01, 0b0000_1111)
        self.tca9537.set_pin_modes(sut.PinMode.INPUT, sut.PinMode.OUTPUT, sut.PinMode.INPUT, sut.PinMode.INPUT)
        # -----------------------------------------------------------------
        # honor request, pin 1 is configured as an output pin
        computed = self.tca9537.set_pin_state(pin=1, is_active=False)
        expected = True
        self.assertEqual(computed, expected)
        # -----------------------------------------------------------------
        with BurstHandler(i2c_bus=self.i2c_bus, i2c_adr=self.i2c_adr) as bh:
            self.assertEqual(bh.read_register(0x01), 0b0000_1101)

    def test_set_invalid_pin(self):
        self.assertRaises(ValueError, self.tca9537.set_pin_state, pin=4, is_active=True)
