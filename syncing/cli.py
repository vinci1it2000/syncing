# -*- coding: utf-8 -*-
#
# Copyright 2019-2021 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
r"""
Define the command line interface.

.. click:: syncing.cli:cli
   :prog: syncing
   :show-nested:

"""
import click
import logging
import click_log
import schedula as sh
import syncing
from syncing._version import __version__
from syncing.model.interp import METHODS

log = logging.getLogger('syncing.cli')


class _Logger(logging.Logger):
    def setLevel(self, level):
        super(_Logger, self).setLevel(level)
        frmt = "%(asctime)-15s:%(levelname)5.5s:%(name)s:%(message)s"
        logging.basicConfig(level=level, format=frmt)
        rlog = logging.getLogger()
        # because `basicConfig()` does not reconfig root-logger when re-invoked.
        rlog.level = level
        logging.captureWarnings(True)


logger = _Logger('cli')
click_log.basic_config(logger)
_process = sh.SubDispatch(syncing.dsp, ['written'], output_type='value')


@click.group(
    'syncing', context_settings=dict(help_option_names=['-h', '--help'])
)
@click.version_option(__version__)
def cli():
    """
    SYNCING command line tool.
    """


@cli.command('template', short_help='Generates sample template file.')
@click.argument(
    'output-file', default='template.xlsx', required=False,
    type=click.Path(writable=True)
)
@click_log.simple_verbosity_option(logger)
def template(output_file='template.xlsx'):
    """
    Writes a sample template OUTPUT_FILE.

    OUTPUT_FILE: SYNCING input template file (.xlsx). [default: ./template.xlsx]
    """
    return _process({'template_fpath': output_file})


@cli.command('sync', short_help='Synchronise and re-sample whole data-sets.')
@click.argument('input-file', type=click.Path(exists=True), nargs=1)
@click.argument('output-file', type=click.Path(writable=True), nargs=1)
@click.argument('data-names', nargs=-1)
@click.option(
    '-R', '--reference-name', help='Reference data-set name.',
    show_default=True
)
@click.option(
    '-x', '--x-label', default=['x'], multiple=True, show_default=True,
    help='Default `var-name` of the common x-axis to synchronise and re-sampled'
         ' the data-sets.'
)
@click.option(
    '-y', '--y-label', default=['y'], multiple=True, show_default=True,
    help='Default `var-name` of the common y-axis to synchronise the data-sets.'
)
@click.option(
    '-I', '--interpolation-method', default='linear',
    type=click.Choice(METHODS), show_default=True,
    help='Interpolation method used to re-sample all data-sets.'
)
@click.option(
    '-S', '--sets-mapping-fpath', type=click.Path(exists=True),
    help='File path (`.json`) of data-sets mapping definition.\n It is like'
         '`{"<set-name>": {"<new-name>": "<old-name>", ...}, ...}`.'
)
@click.option(
    '-L', '--labels-fpath', type=click.Path(exists=True),
    help='File path (`.json`) of `reference-labels` (i.e., "x", "y").\nIt is '
         'like `{"<set-name>": {"x": "<x-label>", "y": "<y-label>"}, ...}`.'
)
@click.option(
    '-M', '--methods-fpath', type=click.Path(exists=True),
    help='File path (`.json`) of interpolation methods.\nIt is like '
         '`{"<set-name>": {"<var-name>": "<interp>", ...}, ...}`.'
)
@click.option(
    '-NS', '--no-sync', is_flag=True,
    help='Executes only the re-sampling without data synchronization.'
)
@click.option(
    '-H', '--header', multiple=True, type=int,
    help='Row (0-indexed) to use for the column labels.'
)
@click_log.simple_verbosity_option(logger)
def sync(input_file, output_file, **kw):
    """
    Synchronise and re-sample data-sets defined in INPUT_FILE and writes shifts
    and synchronized data into the OUTPUT_FILE.

    INPUT_FILE: Data-sets input file (format: .xlsx, .json).

    OUTPUT_FILE: output file (format: .xlsx, .json).

    DATA_NAMES: to filter out the data sets to synchronize.
    """
    kw['x_label'] = sh.bypass(*kw['x_label'])
    kw['y_label'] = sh.bypass(*kw['y_label'])
    kw = {k: v for k, v in kw.items() if v}
    kw['input_fpath'], kw['output_fpath'] = input_file, output_file
    return _process(kw)


if __name__ == '__main__':
    cli()
