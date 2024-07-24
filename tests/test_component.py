#!/usr/bin/env python3
"""
"""

import unittest

import feeph.tca953x as sut


class TestComponent(unittest.TestCase):

    def setUp(self):
        # pretend that extensive setup is required before each test
        self.obj = sut.Component()

    def tearDown(self):
        # nothing to do
        pass

    # ---------------------------------------------------------------------

    def test_case1(self):
        computed = self.obj.do_magic()
        expected = 1
        self.assertEqual(computed, expected)

    def test_case2(self):
        computed = self.obj.do_magic(2)
        expected = 2
        self.assertEqual(computed, expected)
