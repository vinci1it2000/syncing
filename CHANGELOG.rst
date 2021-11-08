Changelog
=========


v1.0.7 (2021-11-08)
-------------------

Feat
~~~~
- (core): Add python 3.9.


Fix
~~~
- (cli): Correct default options.


v1.0.6 (2021-01-04)
-------------------

Fix
~~~
- (rw): Use `openpyxl` to read `xlsx` files.

- (doc): Update copyrights.


v1.0.5 (2020-03-31)
-------------------

Feat
~~~~
- (core): Update build script.

- (test): Add test cases for the new option commands.

- (setup): Update schedula requirement.

- (cli): Add option to execute only the re-sampling.

- (doc): Add code of conduct.

- (github): Add issues and pull requests templates.

- (core): Add support for python 3.8 and drop python 3.5 and drop
  `appveyor`.

- (cli): Add option to filter out the `data-names` to work.


Fix
~~~
- (setup) :gh:`5`: Drop setuptools dependency from `setup.py`

- (cli): Correct logging level.

- (travis): Remove graphviz installation in travis.

- (travis): Correct travis test execution.

- (doc): Correct PEP8.

- (rtd): Add missing requirements.

- (rtd): Correct importing issue.

- (doc): Correct contrib.

- (setup): Add missing test requirements.

- (setup): Remove `nose` from `setup_requires`.

- (build): Improve cleaning.


v1.0.4 (2019-08-21)
-------------------

Feat
~~~~
- (syncing): Remove empty columns.


v1.0.3 (2019-08-20)
-------------------

Feat
~~~~
- (setup) :gh:`3`: Add env `ENABLE_SETUP_LONG_DESCRIPTION`.

- (setup) :gh:`4`: Build as `universal` wheel.

- (write): Add un-synced data to output file.


v1.0.2 (2019-07-15)
-------------------

Fix
~~~
- (setup) :gh:`2`: Correct setup description.


v1.0.1 (2019-07-12)
-------------------

Feat
~~~~
- (cli): Show options defaults.


Fix
~~~
- (setup) :gh:`1`: Update to canonical pypi name of beautifulsoup4.


v1.0.0 (2019-02-23)
-------------------

Feat
~~~~
- (doc): Add sphinx documentation.

- (appveyor, travis): Configure continuous integration.

- (test): Add test cases.

- (setup): Add setup script.

- (doc): Add documentation.

- (cli): Add command line interface.

- (core): Add processing chain model.

- (rw): Add `read` and `write` models.

- (model): Add model.


Fix
~~~
- (test): Ignore errors when deleting temp folder.

- (setup): Correct requirements.

- (test): Skip doctest of DataFrame.

- (test): Correct test case number approx.
