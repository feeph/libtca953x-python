#!/usr/bin/env python3
"""
"""

import unittest

import feeph.tca953x as sut


class TestFunctions(unittest.TestCase):

    def test_case1(self):
        computed = sut.function1()
        expected = 1
        self.assertEqual(computed, expected)

    def test_case2(self):
        computed = sut.function1(2)
        expected = 2
        self.assertEqual(computed, expected)
