.. _start-quick:

#############################################
syncing: Time series synchronization library.
#############################################
|pypi_ver| |travis_status| |cover_status| |docs_status|
|dependencies| |github_issues| |python_ver| |proj_license|

:release:       1.0.7
:date:          2021-11-08 11:00:00
:repository:    https://github.com/vinci1it2000/syncing
:pypi-repo:     https://pypi.org/project/syncing/
:docs:          http://syncing.readthedocs.io/
:wiki:          https://github.com/vinci1it2000/syncing/wiki/
:download:      http://github.com/vinci1it2000/syncing/releases/
:donate:        https://donorbox.org/syncing
:keywords:      data, synchronization, re-sampling
:developers:    .. include:: AUTHORS.rst
:license:       `EUPL 1.1+ <https://joinup.ec.europa.eu/software/page/eupl>`_

.. _start-pypi:
.. _start-intro:

What is syncing?
================
**syncing** is an useful library to synchronise and re-sample time series.

**Synchronization** is based on the **fourier transform** and the
**re-sampling** is performed with a specific interpolation method.

Installation
============
To install it use (with root privileges):

.. code-block:: console

    $ pip install syncing

Or download the last git version and use (with root privileges):

.. code-block:: console

    $ python setup.py install

Install extras
--------------
Some additional functionality is enabled installing the following extras:

- cli: enables the command line interface.
- plot: enables to plot the model process and its workflow.
- dev: installs all libraries plus the development libraries.

To install syncing and all extras (except development libraries), do:

.. code-block:: console

    $ pip install syncing[all]

.. _end-quick:

Synchronising Laboratory Data
=============================
This example shows how to synchronise two data-sets `obd` and `dyno`
(respectively they are the On-Board Diagnostics of a vehicle and Chassis
dynamometer) with a reference signal `ref`. To achieve this we use the
model syncing model to visualize the model:

.. dispatcher:: model
    :opt: graph_attr={'ratio': '1'}
    :code:

    >>> from syncing.model import dsp
    >>> model = dsp.register()
    >>> model.plot(view=False)
    SiteMap(...)

.. tip::
   You can explore the diagram by clicking on it.

First of all, we generate synthetically the data-sets to feed the model:

.. plot::
    :include-source:

    >>> import numpy as np
    >>> data_sets = {}
    >>> time = np.arange(0, 150, .1)
    >>> velocity = (1 + np.sin(time / 10)) * 60
    >>> data_sets['ref'] = dict(
    ...     time=time,                                               # [10 Hz]
    ...     velocity=velocity / 3.6                                  # [m/s]
    ... )
    >>> data_sets['obd'] = dict(
    ...     time=time[::10] + 12,                                    # 1 Hz
    ...     velocity=velocity[::10] + np.random.normal(0, 5, 150),   # [km/h]
    ...     engine_rpm=np.maximum(
    ...         np.random.normal(velocity[::10] * 3 + 600, 5), 800
    ...     )                                                        # [RPM]
    ... )
    >>> data_sets['dyno'] = dict(
    ...     time=time + 6.66,                                        # 10 Hz
    ...     velocity=velocity + np.random.normal(0, 1, 1500)         # [km/h]
    ... )

    To synchronize the data-sets and plot the workflow:

    .. dispatcher:: sol
        :opt: workflow=True, graph_attr={'ratio': '1'}
        :code:

        >>> from syncing.model import dsp
        >>> sol = dsp(dict(
        ...     data=data_sets, x_label='time', y_label='velocity',
        ...     reference_name='ref', interpolation_method='cubic'
        ... ))
        >>> sol.plot(view=False)
        SiteMap(...)

    Finally, we can analyze the time shifts and the synchronized and re-sampled
    data-sets:

    >>> import pandas as pd
    >>> import schedula as sh
    >>> pd.DataFrame(sol['shifts'], index=[0])  # doctest: +SKIP
         obd  dyno
    ...
    >>> df = pd.DataFrame(dict(sh.stack_nested_keys(sol['resampled'])))
    >>> df.columns = df.columns.map('/'.join)
    >>> df['ref/velocity'] *= 3.6
    >>> ax = df.set_index('ref/time').plot(secondary_y='obd/engine_rpm')
    >>> ax.set_ylabel('[km/h]'); ax.right_ax.set_ylabel('[RPM]')
    Text(...)

.. _end-pypi:
.. _end-intro:
.. _start-badges:
.. |travis_status| image:: https://travis-ci.org/vinci1it2000/syncing.svg?branch=master
    :alt: Travis build status
    :target: https://travis-ci.org/vinci1it2000/syncing

.. |cover_status| image:: https://coveralls.io/repos/github/vinci1it2000/syncing/badge.svg?branch=master
    :target: https://coveralls.io/github/vinci1it2000/syncing?branch=master
    :alt: Code coverage

.. |docs_status| image:: https://readthedocs.org/projects/syncing/badge/?version=stable
    :alt: Documentation status
    :target: https://syncing.readthedocs.io/en/stable/?badge=stable

.. |pypi_ver| image::  https://img.shields.io/pypi/v/syncing.svg?
    :target: https://pypi.python.org/pypi/syncing/
    :alt: Latest Version in PyPI

.. |python_ver| image:: https://img.shields.io/pypi/pyversions/syncing.svg?
    :target: https://pypi.python.org/pypi/syncing/
    :alt: Supported Python versions

.. |github_issues| image:: https://img.shields.io/github/issues/vinci1it2000/syncing.svg?
    :target: https://github.com/vinci1it2000/syncing/issues
    :alt: Issues count

.. |proj_license| image:: https://img.shields.io/badge/license-EUPL%201.1%2B-blue.svg?
    :target: https://raw.githubusercontent.com/vinci1it2000/syncing/master/LICENSE.txt
    :alt: Project License

.. |dependencies| image:: https://img.shields.io/requires/github/vinci1it2000/syncing.svg?
    :target: https://requires.io/github/vinci1it2000/syncing/requirements/?branch=master
    :alt: Dependencies up-to-date?
.. _end-badges:
