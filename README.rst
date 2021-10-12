Send tweet via Ham RADIO!
=========================

|PyPI| |Status| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit|

.. |PyPI| image:: https://img.shields.io/pypi/v/aprsd-twitter-plugin.svg
   :target: https://pypi.org/project/aprsd-twitter-plugin/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/aprsd-twitter-plugin.svg
   :target: https://pypi.org/project/aprsd-twitter-plugin/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/aprsd-twitter-plugin
   :target: https://pypi.org/project/aprsd-twitter-plugin
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/aprsd-twitter-plugin
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/aprsd-twitter-plugin/latest.svg?label=Read%20the%20Docs
   :target: https://aprsd-twitter-plugin.readthedocs.io/
   :alt: Read the documentation at https://aprsd-twitter-plugin.readthedocs.io/
.. |Tests| image:: https://github.com/hemna/aprsd-twitter-plugin/workflows/Tests/badge.svg
   :target: https://github.com/hemna/aprsd-twitter-plugin/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/hemna/aprsd-twitter-plugin/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/hemna/aprsd-twitter-plugin
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit


Features
--------

* Sent a tweet from your personal twitter account!
* to tweet send a message of "t Hello World #aprs #hamradio"


Requirements
------------

* This plugin requires you have a twitter account and create a developer
  account with:
* api key
* api key secret
* access token
* access token secret

Add the following entries to the aprsd.yml file

.. code:: yaml

    services:
      twitter:
        apiKey: <your api key here>
        apiKey_secret: <your api key secret here>
        access_token: <your Twitter app access token>
        access_token_secret: <your Twitter app access token secret>


Installation
------------

You can install *Send tweet via Ham RADIO!* via pip_ from PyPI_:

.. code:: console

   $ pip install aprsd-twitter-plugin


Usage
-----

Please see the `Command-line Reference <Usage_>`_ for details.


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `MIT license`_,
*Send tweet via Ham RADIO!* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from `@hemna`_'s `APRSD Plugin Python Cookiecutter`_ template.

.. _@hemna: https://github.com/hemna
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _MIT license: https://opensource.org/licenses/MIT
.. _PyPI: https://pypi.org/
.. _APRSD Plugin Python Cookiecutter: https://github.com/hemna/cookiecutter-aprsd-plugin
.. _file an issue: https://github.com/hemna/aprsd-twitter-plugin/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
.. _Usage: https://aprsd-twitter-plugin.readthedocs.io/en/latest/usage.html
