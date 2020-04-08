# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2019-2021 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It contains utility functions to read and write input/output files.

Sub-Modules:

.. currentmodule:: syncing.rw

.. autosummary::
    :nosignatures:
    :toctree: rw/

    read
    write
"""


def file_ext(*ext):
    """
    Define a function to check file extensions.

    :param ext:
        Allowed extensions.
    :type ext: str

    :return:
        Function to check file extensions.
    :rtype: function
    """
    ext = tuple('.%s' % k for k in ext)

    # noinspection PyUnusedLocal
    def domain(fpath, *args):
        return fpath.lower().endswith(ext)

    return domain
