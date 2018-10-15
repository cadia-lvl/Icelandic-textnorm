#!/usr/bin/env python3
# -*- coding: utf-8 -*-



class Cardinal:

    def __init__(self, val, preserve_ord=False):
        self.integer = val
        self.preserve_order = preserve_ord

    def __str__(self):
        return 'Cardinal integer: ' + self.integer