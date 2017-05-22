============================================
Knobs are used to tune environment variables
============================================


.. image:: https://badge.fury.io/py/knobs.svg
   :target: https://badge.fury.io/py/knobs


.. image:: https://readthedocs.org/projects/knobs/badge/?version=latest
   :target: http://knobs.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

|
|

.. image:: https://github.com/sthysel/knobs/blob/master/docs/knob.jpg?raw=true


.. code:: python

   >>> pirates = Knob('JOLLY_ROGER_PIRATES', 124, description='Yar')
   >>> pirates.get()
   124
   >>> pirates.get_type()
   >>> <type 'int'>


Use ``knobs`` if you worship at the church of the `12 Factor App <http://www.12factor.net/>`_

A knob is a wrapper for an environment variable. It can:

* Read and write an environment variable
* Make sure it is of the expected type
* Validate a value is good.


``knobs`` will search for a nominated environmental file (default ``.env``) and load that
into the environment. A knob is type aware, configured from the environment and its value can be
persisted to ease the creation of configuration files.




Install
=======

Install from pypi

.. code::

   $ pip install knobs

Install from source

.. code::

   $ pip install .



Versioning
==========

Current version is 0.2.10
