#!/usr/bin/env python3
"""
TCA9537 - 4-Bit I²C I/O Expander with Configuration Registers

datasheet: # https://www.ti.com/lit/ds/symlink/tca9537.pdf
"""

from enum import Enum


class PinMode(Enum):
    """
    define the pin as an input or output pin
    """
    OUTPUT = 0
    INPUT = 1


class PinPolarity(Enum):
    """
    define the relation of logical value to output level
     - matching: value = 0 -> pin = low
     - inverted: value = 0 -> pin = high
    """
    MATCHING = 0  # value: 1 -> pin: high
    INVERTED = 1  # value: 0 -> pin: high
