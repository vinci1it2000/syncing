# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It contains functions and a model `dsp` to read input files.
"""
import schedula as sh
from . import file_ext

dsp = sh.BlueDispatcher(name='read_data', raises=True)


@sh.add_function(dsp, outputs=['sets_mapping'], input_domain=file_ext('json'))
def load_sets_mapping(sets_mapping_fpath):
    """
    Load the mapping of data-sets to _process.

    :param sets_mapping_fpath:
        File path (`.json`) of the mapping of data-sets to _process.

        It is like `{"<set-name>": {"<new-name>": "<old-name>", ...}, ...}`.
    :type sets_mapping_fpath: str

    :return:
        Mapping of data-sets to _process.

        It is like `{"<set-name>": {"<new-name>": "<old-name>", ...}, ...}`.
    :rtype: dict[str, str]
    """
    import json
    with open(sets_mapping_fpath) as f:
        return json.load(f)


@sh.add_function(dsp, outputs=['labels'], input_domain=file_ext('json'),
                 inputs_kwargs=True, inputs_defaults=True)
def load_reference_labels(labels_fpath, x_label='x', y_label='y'):
    """
    Load `reference-labels` (i.e., "x", "y") for each data-set.

    :param labels_fpath:
        File path (`.json`) of `reference-labels` (i.e., "x", "y").

        It is like `{"<set-name>": {"x": "<x-label>", "y": "<y-label>"}, ...}`.
    :type labels_fpath: str

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
    import json
    from syncing.model import define_labels
    with open(labels_fpath) as f:
        labels = define_labels(x_label, y_label)
        labels.update(json.load(f))
        return labels


@sh.add_function(dsp, outputs=['methods'], inputs_kwargs=True,
                 inputs_defaults=True)
def load_interpolation_methods(methods_fpath, interpolation_method='linear'):
    """
    Load interpolation methods for each variable of each data-set.

    :param methods_fpath:
        File path (`.json`) of interpolation methods.

        It is like `{"<set-name>": {"<var-name>": "<interp>", ...}, ...}`.
    :type methods_fpath: str

    :param interpolation_method:
        Default interpolation method.
    :type interpolation_method: str

    :return:
        Interpolation methods for each variable of each data-set.

        It is like `{"<set-name>": {"<var-name>": "<interp>", ...}, ...}`.
    :rtype: collections.defaultdict
    """
    import json
    from syncing.model.interp import METHODS
    from syncing.model import define_interpolation_methods
    with open(methods_fpath) as f:
        methods = define_interpolation_methods(interpolation_method)
        for k, v in sh.stack_nested_keys(json.load(f)):
            methods[k[0]][sh.bypass(*k[1:])] = METHODS[v]
        return methods


dsp.add_data('reference_name', description='Reference data-set name.')


@sh.add_function(dsp, outputs=['raw_data', 'reference_name'],
                 inputs_kwargs=True, inputs_defaults=True,
                 input_domain=file_ext('xlsx', 'xls'))
def read_excel(input_fpath, header=0):
    """
    Reads the excel file.

    :param input_fpath:
        Input file path.
    :type input_fpath: str

    :param header:
        Row (0-indexed) to use for the column labels.
    :type header: str

    :return:
        Raw data-sets and reference data-set name.
    :rtype: dict[str, dict[str, numpy.array]], str
    """
    import pandas as pd
    with pd.ExcelFile(input_fpath) as xls:
        data, names = {}, xls.book.sheet_names()
        for sheet_name, df in pd.read_excel(xls, names, header).items():
            if not df.empty:
                data[sheet_name] = {k: v.values for k, v in df.items()}
                if isinstance(header, tuple) and len(header) > 1 and \
                        any(c is not None for c in df.columns.names):
                    data[sheet_name][tuple(df.columns.names)] = df.index.values
        return data, names[0]


@sh.add_function(dsp, outputs=['raw_data'], input_domain=file_ext('json'))
def read_json(input_fpath):
    """
    Reads the json file.

    :param input_fpath:
        Input file path.
    :type input_fpath: str

    :return:
        Raw data-sets.
    :rtype: dict[str, dict[str, numpy.array]]
    """
    import json
    import numpy as np
    data = {}
    with open(input_fpath) as file:
        for k, v in sh.stack_nested_keys(json.load(file)):
            sh.get_nested_dicts(data, k[0])[sh.bypass(*k[1:])] = np.array(v)
        return data
