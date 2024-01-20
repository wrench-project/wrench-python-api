#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

class WRENCHException(Exception):
    """
    Minimal exception class
    """

    def __init__(self, message: str) -> None:
        """
        Constructor

        :param message: Exception message
        :type message: str
        """
        super().__init__(message)

    pass
