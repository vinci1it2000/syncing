# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2019-2021 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It contains utility functions and the computational model `dsp` to synchronise
and re-sample data-sets.

Sub-Modules:

.. currentmodule:: syncing.model

.. autosummary::
    :nosignatures:
    :toctree: model/

    interp
"""
import schedula as sh

#: Computational Model.
dsp = sh.BlueDispatcher(name='Computational Model', raises=True)


@sh.add_function(dsp, outputs=['labels'], inputs_kwargs=True,
                 inputs_defaults=True)
def define_labels(x_label='x', y_label='y'):
    """
    Defines `reference-labels` (i.e., "x", "y") for each data-set.

    :param x_label:
        Default `var-name` of the common x-axis to synchronise and re-sampled
        the data-sets.
    :type x_label: str

    :param y_label:
        Default `var-name` of the common y-axis to synchronise the data-sets.
    :type y_label: str

    :return:
        Reference-labels (i.e., "x", "y") for each data-set.

        It is like `{"<set-name>": {"x": "<x-label>", "y": "<y-label>"}, ...}`.
    :rtype: collections.defaultdict
    """
    import collections
    return collections.defaultdict(lambda: dict(x=x_label, y=y_label))


def _get(labels, name, data, *keys):
    labels = labels[name]
    return [data[labels[key]] for key in keys]


# noinspection PyPep8Naming
def _compute_shifts(ref, *data):
    import numpy as np
    import numpy.fft as fft

    l, h = zip(*((x.min(), x.max()) for x, y in (ref,) + data))
    l, h = min(l), max(h)

    dx = float(np.median(np.diff(ref[0])) / 10)

    X = np.arange(l, h + dx, dx)
    Y = np.interp(X, *ref)

    zero_index, f1 = int(len(Y) / 2) - 1, fft.fft(Y)
    for x, y in data:
        f2 = fft.fft(np.flipud(np.interp(X, x, y)))
        c = fft.fftshift(np.real(fft.ifft(f1 * f2)))
        assert len(c) == len(Y)
        yield float((zero_index - np.argmax(c)) * dx)


@sh.add_function(
    dsp, inputs_kwargs=True, inputs_defaults=True, outputs=['shifts']
)
def calculate_shifts(labels, reference_name, data, no_sync=False):
    """
    Calculates the shifts from the reference data-set.

    :param labels:
        Reference-labels (i.e., "x", "y") for each data-set.

        It is like `{"<set-name>": {"x": "<x-label>", "y": "<y-label>"}, ...}`.
    :type labels: collections.defaultdict

    :param reference_name:
        Reference data-set name.
    :type reference_name: str

    :param data:
        Data-sets.
    :type data: dict[str, dict[str, numpy.array]]

    :param no_sync:
        Skip the data synchronization?
    :type no_sync: bool

    :return:
        Shifts from the reference data-set.
    :rtype: dict[str, float]
    """
    keys = [k for k in data if k != reference_name]
    if no_sync:
        return dict.fromkeys(keys, 0)
    data = {k: _get(labels, k, v, 'x', 'y') for k, v in data.items()}
    args = sh.selector([reference_name] + keys, data, output_type='list')
    return sh.map_list(keys, *_compute_shifts(*args))


def _interpolate(x, x_label, data, methods):
    xp = data[x_label]
    return {
        k: methods[k](x, xp=xp, fp=v) for k, v in data.items() if k != x_label
    }


@sh.add_function(dsp, outputs=['methods'], inputs_kwargs=True,
                 inputs_defaults=True, weight=sh.inf(1, 0))
def define_interpolation_methods(interpolation_method='linear'):
    """
    Defines interpolation methods for each variable of each data-set.

    :param interpolation_method:
        Default interpolation method.
    :type interpolation_method: str

    :return:
        Interpolation methods for each variable of each data-set.

        It is like `{"<set-name>": {"<var-name>": "<interp>", ...}, ...}`.
    :rtype: collections.defaultdict
    """
    import collections
    from .interp import METHODS
    method = METHODS[interpolation_method]
    default = collections.defaultdict(lambda: method)
    return collections.defaultdict(lambda: default)


@sh.add_function(dsp, outputs=['resampled'])
def resample_data(labels, reference_name, data, shifts, methods):
    """
    Resample all data-sets using the reference signal.

    :param labels:
        Reference-labels (i.e., "x", "y") for each data-set.

        It is like `{"<set-name>": {"x": "<x-label>", "y": "<y-label>"}, ...}`.
    :type labels: collections.defaultdict

    :param reference_name:
        Reference data-set name.
    :type reference_name: str

    :param data:
        Data-sets.
    :type data: dict[str, dict[str, numpy.array]]

    :param shifts:
        Shifts from the reference data-set.
    :type shifts: dict[str, float]

    :param methods:
        Interpolation methods for each variable of each data-set.

        It is like `{"<set-name>": {"<var-name>": "<interp>", ...}, ...}`.
    :type methods: collections.defaultdict

    :return:
        Resampled data-sets.
    :rtype: dict[str, dict[str, numpy.array]]
    """
    x = data[reference_name][labels[reference_name]['x']]
    r, res = {reference_name: data[reference_name]}, {}
    for k, s in shifts.items():
        r[k] = _interpolate(x + s, labels[k]['x'], data[k], methods[k])

    for (i, j), v in sh.stack_nested_keys(r):
        j = sh.stlp(j)
        sh.get_nested_dicts(res, i, *j[:-1])[j[-1]] = v

    return res
