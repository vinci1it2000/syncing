# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2019-2021 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It contains utility functions and methods to interpolate the data-sets.
"""
import functools
import numpy as np
import scipy.interpolate as sci_itp


def _interp_wrapper(func, x, xp, fp, **kw):
    if isinstance(kw.get('fill_value'), tuple) and not kw['fill_value']:
        kw['fill_value'] = fp[0], fp[-1]
    return np.nan_to_num(func(xp, fp, **kw)(x))


def polynomial_interpolation(x, xp, fp, order=1):
    """
    Re-samples data using the polynomial interpolation.

    :param x:
        The x-coordinates of the re-sampled values.
    :type x: numpy.array

    :param xp:
        The x-coordinates of the data points.
    :type xp: numpy.array

    :param fp:
        The y-coordinates of the data points, same length as xp.
    :type fp: numpy.array

    :param order:
        Polynomial order.
    :type order: int

    :return:
        Re-sampled y-values.
    :rtype: numpy.array
    """
    return np.poly1d(np.polyfit(xp, fp, order))(x)


# noinspection PyPep8Naming
def _cum_integral(x, xp, fp):
    from scipy.integrate import cumtrapz
    X = np.unique(np.concatenate((x, xp)))
    Y = np.interp(X, xp, fp, left=0.0, right=0.0)
    return cumtrapz(Y, X, initial=0)[np.searchsorted(X, x)]


# noinspection PyPep8Naming
def integral_interpolation(x, xp, fp):
    """
    Re-samples data maintaining the signal integral.

    :param x:
        The x-coordinates of the re-sampled values.
    :type x: numpy.array

    :param xp:
        The x-coordinates of the data points.
    :type xp: numpy.array

    :param fp:
        The y-coordinates of the data points, same length as xp.
    :type fp: numpy.array

    :return:
        Re-sampled y-values.
    :rtype: numpy.array
    """

    x, fp = np.asarray(x, dtype=float), np.asarray(fp, dtype=float)
    xp = np.asarray(xp, dtype=float)
    n = len(x)
    X, dx = np.zeros(n + 1), np.zeros(n + 1)
    dx[1:-1] = np.diff(x)
    X[0], X[1:-1], X[-1] = x[0], x[:-1] + dx[1:-1] / 2, x[-1]
    integral_matrix = np.diff(_cum_integral(X, xp, fp))

    dx /= 8.0
    # noinspection PyTypeChecker
    A = np.diag((dx[:-1] + dx[1:]) * 3.0)
    i, j = np.indices(A.shape)
    A[i == j - 1] = A[i - 1 == j] = dx[1:-1]

    return np.linalg.solve(A, integral_matrix)


METHODS = ('linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic')
_kw = dict(fill_value=(), copy=False, bounds_error=False)
METHODS = {
    k: functools.partial(_interp_wrapper, sci_itp.interp1d, kind=k, **_kw)
    for k in METHODS
}
METHODS['pchip'] = functools.partial(
    _interp_wrapper, sci_itp.PchipInterpolator
)
METHODS['akima'] = functools.partial(
    _interp_wrapper, sci_itp.Akima1DInterpolator
)
METHODS['integral'] = integral_interpolation
for k in range(5):
    METHODS['polynomial%d' % k] = functools.partial(
        polynomial_interpolation, order=k
    )

for k in range(5, 10, 2):
    METHODS['spline%d' % k] = functools.partial(
        _interp_wrapper, sci_itp.interp1d, kind=k, **_kw
    )
