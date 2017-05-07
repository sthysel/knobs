Knobs are used to tune environment variables
============================================

.. image:: pics/knob.jpg

Use *knobs* if you worship at the church of the `12 Factor App <http://www.12factor.net/>`_

A knob is a wrapper for an environment variable. It can
* Read and write an environment variable
* Make sure it is of the expected type
* Validate a value is good.

*knobs* will search for a nominated environmental file (default *.env*) and load that
into the environment. A knob is type aware, configured from the environment and its value can be
persisted to ease the creation of configuration files.

Knobs uses a forked copy of [python-sotenv](https://github.com/theskumar/python-dotenv)


Install
*******


Install from source ``pip install .``




