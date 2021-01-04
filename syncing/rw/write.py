# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2019-2021 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It contains functions and a model `dsp` to write output data into files.
"""
import os
import os.path as osp
import schedula as sh
from . import file_ext

#: Write Model.
dsp = sh.BlueDispatcher(name='write_data', raises=True)


@sh.add_function(dsp, input_domain=file_ext('xlsx'), outputs=['written'])
def save_excel_template(template_fpath):
    """
    Save template as excel.

    :param template_fpath:
        Template file path.
    :type template_fpath: str
    """
    import pandas as pd
    os.makedirs(osp.dirname(template_fpath) or '.', exist_ok=True)
    with pd.ExcelWriter(template_fpath, engine='openpyxl') as writer:
        pd.DataFrame(
            {'x': [], 'y': []}, index=[]
        ).to_excel(writer, 'ref', index=False)
        pd.DataFrame(
            {'x': [], 'y': [], 'data-1': [], 'data-2': []}, index=[]
        ).to_excel(writer, 'data', index=False)
    return template_fpath


@sh.add_function(dsp, input_domain=file_ext('xlsx'), outputs=['written'])
def save_excel(output_fpath, outputs):
    """
    Save dsp outputs in an Excel file.

    :param output_fpath:
        Output file path.
    :type output_fpath: str

    :param outputs:
        Model outputs.
    :type outputs: dict

    :return:
        File path where output are written.
    :rtype: str
    """
    import pandas as pd
    os.makedirs(osp.dirname(output_fpath) or '.', exist_ok=True)
    with pd.ExcelWriter(output_fpath, engine='openpyxl') as writer:
        if 'shifts' in outputs:
            pd.DataFrame(outputs['shifts'], index=[0]).T.to_excel(
                writer, 'shifts', header=False
            )
        if 'resampled' in outputs:
            data = dict(sh.stack_nested_keys(outputs['resampled']))
            pd.DataFrame(data).to_excel(writer, 'synced')

        for name, data in outputs.get('data', {}).items():
            pd.DataFrame(data).to_excel(writer, 'origin.%s' % name)
    return output_fpath


def _json_default(o):
    import numpy as np
    if isinstance(o, np.ndarray):
        return o.tolist()


@sh.add_function(dsp, input_domain=file_ext('json'), outputs=['written'])
def save_json(output_fpath, outputs):
    """
    Save dsp outputs in an JSON file.

    :param output_fpath:
        Output file path.
    :type output_fpath: str

    :param outputs:
        Model outputs.
    :type outputs: dict

    :return:
        File path where output are written.
    :rtype: str
    """
    import json
    os.makedirs(osp.dirname(output_fpath) or '.', exist_ok=True)
    with open(output_fpath, 'w') as file:
        json.dump(
            sh.selector(('shifts', 'resampled'), outputs, allow_miss=True),
            file, default=_json_default
        )
    return output_fpath
