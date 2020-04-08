# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2019-2021 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Defines the file processing chain model `dsp`.

Sub-Modules:

.. currentmodule:: syncing

.. autosummary::
    :nosignatures:
    :toctree: syncing/

    model
    rw
    cli
"""
import numpy as np
import functools
import schedula as sh
from syncing._version import *
from syncing import model
from syncing.rw import read, write

#: Processing Model.
dsp = sh.BlueDispatcher(name='Processing Model', raises=True)

dsp.add_data('interpolation_method', 'linear')
dsp.add_dispatcher(
    read.dsp,
    inputs=['input_fpath', 'header', 'sets_mapping_fpath', 'labels_fpath',
            'methods_fpath', 'interpolation_method', 'x_label', 'y_label',
            'data_names'],
    outputs=['raw_data', 'reference_name', 'sets_mapping', 'labels', 'methods']
)


@sh.add_function(dsp, inputs_kwargs=True, outputs=['data'])
def parse_data(raw_data, sets_mapping=None):
    """
    Extract and rename the data-sets to _process.

    :param raw_data:
        Raw Data.
    :type raw_data: dict[str, dict[str, numpy.array]]

    :param sets_mapping:
        Mapping of data-sets to _process.

        It is like `{"<set-name>": {"<new-name>": "<old-name>", ...}, ...}`.
    :type sets_mapping: dict[str, dict[str, str]]

    :return:
        Model data.
    :rtype: dict
    """
    if sets_mapping is None:
        data = raw_data
    else:
        data = {}
        for (i, j), k in sh.stack_nested_keys(sets_mapping):
            sh.get_nested_dicts(data, i)[j] = raw_data[i][k]
    parsed_data = {}
    for (i, j), v in sh.stack_nested_keys(data):
        if not np.isnan(v).all():
            sh.get_nested_dicts(parsed_data, i)[j] = v
    return parsed_data


dsp.add_data('x_label', 'x')
dsp.add_data('y_label', 'y')
dsp.add_data('labels', None, sh.inf(1, 0))
dsp.add_data('methods', None, sh.inf(1, 0))
dsp.add_data('sets_mapping', None, sh.inf(1, 0))
dsp.add_data('no_sync', False)
input_keys = [
    'methods', 'data', 'reference_name', 'labels', 'x_label', 'y_label',
    'interpolation_method', 'no_sync'
]

dsp.add_function(
    function_id='map_inputs',
    function=functools.partial(sh.map_list, input_keys),
    filters=[lambda x: {k: v for k, v in x.items() if v is not None}],
    inputs=input_keys,
    outputs=['inputs']
)

dsp.add_function(
    function_id='compute_outputs',
    function=sh.SubDispatch(model.dsp),
    inputs=['inputs'],
    outputs=['outputs'],
    description='Executes the computational model.'
)

dsp.add_dispatcher(
    write.dsp,
    inputs=['outputs', 'output_fpath', 'template_fpath'],
    outputs=['written']
)
