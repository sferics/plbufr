plbufr
======

TODO (these links do not exist yet!)
.. image:: https://img.shields.io/pypi/v/plbufr.svg
   :target: https://pypi.python.org/pypi/plbufr/


*plbufr* is a Python package implementing a `Polars <https://github.com/pola-rs/polars>`_ reader (instead of pdbufr's Pandas) for the BUFR format using  `ecCodes <https://confluence.ecmwf.int/display/ECC>`_. Its goal is to be faster and more versatile than `pdbufr <https://github.com/ecmwf/pdbufr>`_. Therefore, it will implement more features like filtering of missing data which is currently not supported by pdbufr. It supports BUFR edition 3 and 4 files with uncompressed and compressed subsets. It works on Linux, MacOS and Windows, the ecCodes C-library is the only binary dependency. All modern versions of Python (>=3.6) and PyPy3 are supported.

TODO
The documentation will be found at https://plbufr.readthedocs.io/.


License
=======

Copyright 2019- European Centre for Medium-Range Weather Forecasts (ECMWF).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0.
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
