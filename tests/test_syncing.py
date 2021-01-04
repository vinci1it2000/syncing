#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2019-2021 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import os
import ddt
import json
import shutil
import unittest
import numpy as np
import pandas as pd
import os.path as osp
import schedula as sh
from click.testing import CliRunner
import syncing.cli as cli

test_dir = osp.dirname(__file__)
files_dir = osp.join(test_dir, 'files')
results_dir = osp.join(test_dir, 'results')
files = dict(
    xl=osp.join(test_dir, 'files', 'data.xlsx'),
    json=osp.join(test_dir, 'files', 'data.json'),
    methods=osp.join(test_dir, 'files', 'methods.json'),
    sets=osp.join(test_dir, 'files', 'sets.json'),
    labels=osp.join(test_dir, 'files', 'labels.json'),
    xl_H=osp.join(test_dir, 'files', 'data_H.xlsx'),
)


@ddt.ddt
class TestCMD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = osp.join(test_dir, 'temp')
        cls.runner = CliRunner()
        shutil.rmtree(cls.temp, ignore_errors=True)
        os.makedirs(cls.temp, exist_ok=True)
        os.chdir(cls.temp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp, ignore_errors=True)

    @ddt.idata((
            ([], 2, 0),
            ([files['xl'], 'none.xlsx'], 1, 0),
            ([files['xl'], 'sync.xlsx', '-y', 'y1'], 0, 1),
            ([files['xl'], 'sync.json', '-y', 'y1'], 0, 1),
            ([files['json'], 'none.json', '-y', 'y1'], 1, 0),
            ([files['json'], 'sync1.xlsx', '-y', 'y1', '-R', 'Sheet2'], 0, 1),
            ([files['xl'], 'sync1.json', '-y', 'y1', '-I', 'cubic'], 0, 1),
            ([files['xl'], 'sync2.xlsx', '-I', 'cubic', '-M', files['methods'],
              '-S', files['sets'], '-L', files['labels']], 0, 1),
            ([files['xl'], 'sync2.json', '-I', 'cubic', '-M', files['methods'],
              '-S', files['sets'], '-L', files['labels']], 0, 1),
            ([files['xl_H'], 'sync3.xlsx', '-H', 0, '-H', 1,
              '-x', 'x', '-x', 'x', '-y', 'y', '-y', 'y'], 0, 1),
            ([files['xl_H'], 'sync3.json', '-H', 0, '-H', 1,
              '-x', 'x', '-x', 'x', '-y', 'y', '-y', 'y'], 0, 1),
            ([files['xl'], 'sync4.xlsx', '-y', 'y1', '-NS'], 0, 1),
            ([files['xl'], 'sync4.json', '-y', 'y1', '-NS'], 0, 1),
            ([files['xl'], 'sync5.xlsx', 'Sheet2', 'Sheet1', '-y', 'y1'], 0, 1),
            ([files['xl'], 'sync5.json', 'Sheet2', 'Sheet1', '-y', 'y1'], 0, 1),
    ))
    def test_sync(self, data):
        args, exit_code, file = data
        self.maxDiff = None
        result = self.runner.invoke(cli.sync, args)
        self.assertEqual(exit_code, result.exit_code, result)
        if file:
            self.assertTrue(osp.isfile(args[1]))
            res = osp.join(results_dir, args[1])
            if osp.isfile(res):
                with open(res) as e, open(args[1]) as r:
                    self.assertEqual({
                        k: np.round(v, 7).tolist()
                        for k, v in sh.stack_nested_keys(json.load(e))
                    }, {
                        k: np.round(v, 7).tolist()
                        for k, v in sh.stack_nested_keys(json.load(r))
                    })

    @ddt.idata((
            ([], 0, cli.template.params[0].default),
            (['sub/template.xlsx'], 0, 'sub/template.xlsx'),
            (['sub/none.txt'], 1, None)
    ))
    def test_template(self, data):
        args, exit_code, file = data
        result = self.runner.invoke(cli.template, args)
        self.assertEqual(exit_code, result.exit_code)
        if exit_code == 0:
            self.assertTrue(osp.isfile(file))
            with pd.ExcelFile(file, engine='openpyxl') as xl:
                self.assertEqual({'ref', 'data'}, set(xl.sheet_names))
                self.assertEqual(
                    {'x', 'y'}, set(pd.read_excel(xl, 'ref').columns)
                )
                self.assertEqual(
                    {'x', 'y', 'data-1', 'data-2'},
                    set(pd.read_excel(xl, 'data').columns)
                )
