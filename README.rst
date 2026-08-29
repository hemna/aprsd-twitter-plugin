Post to X (formerly Twitter) via Ham Radio APRS!
=================================================

|PyPI| |Status| |Python Version| |License| |pre-commit|

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
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit


Overview
--------

``aprsd-twitter-plugin`` is an `APRSD <https://github.com/craigerl/aprsd>`_
plugin that lets a licensed amateur radio operator post to X (formerly Twitter)
directly from a radio by sending an APRS message.

Send ``tw Hello from the shack! #hamradio`` over APRS and it appears on X.

.. note::

   **A paid X developer account is required.**  X ended free API v1.1 write
   access in February 2023.  You need at least the **Basic** tier on the
   `X Developer Portal <https://developer.x.com/en/portal/dashboard>`_ to
   obtain write-capable OAuth 1.0a credentials.  Read access (and therefore
   read-only bearer tokens) is not sufficient — this plugin posts tweets.


Features
--------

* Post to X from any APRS client — HT, mobile rig, Winlink, APRS.fi, etc.
* Only a configurable callsign (and its SSIDs) is authorised to post.
* Optionally appends ``#aprs #aprsd #hamradio`` and the project URL to every
  post.
* Uses the **X API v2** via ``tweepy.Client`` — the only supported API for
  write access since 2023.


Requirements
------------

* Python 3.9 or later
* `APRSD <https://github.com/craigerl/aprsd>`_ (installed separately)
* `tweepy <https://www.tweepy.org/>`_ >= 4.0
* A **paid X developer account** with an app that has *read + write*
  OAuth 1.0a permissions

Credentials needed
~~~~~~~~~~~~~~~~~~

From the `X Developer Portal → Keys and tokens
<https://developer.x.com/en/portal/dashboard>`_ for your app:

+------------------------------+----------------------------------------------+
| Config key                   | Where to find it                             |
+==============================+==============================================+
| ``apiKey``                   | *API Key* (Consumer Key)                     |
+------------------------------+----------------------------------------------+
| ``apiKey_secret``            | *API Key Secret* (Consumer Secret)           |
+------------------------------+----------------------------------------------+
| ``access_token``             | *Access Token* (generate under Keys/Tokens)  |
+------------------------------+----------------------------------------------+
| ``access_token_secret``      | *Access Token Secret*                        |
+------------------------------+----------------------------------------------+

.. important::

   Make sure the app's **User authentication settings** are set to
   *Read and Write* (not just *Read*).  Without write permissions the plugin
   will return ``Failed: no write permission``.


Installation
------------

.. code:: console

   $ pip install aprsd-twitter-plugin


Configuration
-------------

Add an ``aprsd_twitter_plugin`` section to your ``aprsd.yml``:

.. code:: yaml

    aprsd_twitter_plugin:
      # Callsign allowed to post.  Any SSID of this callsign is also allowed
      # (e.g. WB4BOR-1, WB4BOR-9).
      callsign: WB4BOR

      # OAuth 1.0a credentials — obtain from developer.x.com
      apiKey: <your API Key / Consumer Key>
      apiKey_secret: <your API Key Secret / Consumer Secret>
      access_token: <your Access Token>
      access_token_secret: <your Access Token Secret>

      # Set false to suppress automatic hashtag/URL appending (default: true)
      add_aprs_hashtag: true

.. warning::

   Never commit your credentials to version control.  Keep ``aprsd.yml``
   out of git (add it to ``.gitignore``).


Usage
-----

From your APRS client send a message to your APRSD station:

.. code::

   tw <your message here>

   # or
   twitter <your message here>

Examples::

   tw Hello from the ham shack! Grid DM79
   tw Just worked JA on 20m SSB #hamradio

With ``add_aprs_hashtag: true`` (default) the plugin automatically appends::

   #aprs #aprsd #hamradio http://git.hemna.com/hemna/aprsd-twitter-plugin

Keep your total message under 280 characters to avoid truncation by X.

**Response messages**

+------------------------------------------+-----------------------------+
| Plugin response                          | Meaning                     |
+==========================================+=============================+
| ``Post sent!``                           | Success                     |
+------------------------------------------+-----------------------------+
| ``<CALLSIGN> not authorized to post!``   | Sender not in allow-list    |
+------------------------------------------+-----------------------------+
| ``Failed: no write permission``          | App lacks write permissions |
+------------------------------------------+-----------------------------+
| ``Failed to post``                       | Other X API error           |
+------------------------------------------+-----------------------------+
| ``Failed to create client``              | Credential/config error     |
+------------------------------------------+-----------------------------+


Contributing
------------

Contributions are welcome!

* Source: https://github.com/hemna/aprsd-twitter-plugin
* Issues: https://github.com/hemna/aprsd-twitter-plugin/issues

To set up a development environment::

   git clone https://github.com/hemna/aprsd-twitter-plugin.git
   cd aprsd-twitter-plugin
   pip install -e ".[dev]"
   pre-commit install

Run the test suite::

   pytest tests/ -v


License
-------

Distributed under the terms of the `MIT License`_.

.. _MIT License: https://opensource.org/licenses/MIT
