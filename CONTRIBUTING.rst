Contributing
------------

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
https://github.com/spatialaudio/python-pa-ringbuffer/.
Contributions are always welcome!

Instead of pip-installing the latest release from PyPI_, you should get the
newest development version with Git::

   git clone https://github.com/spatialaudio/python-pa-ringbuffer.git
   cd python-sounddevice
   python3 setup.py develop --user

.. _PyPI: https://pypi.python.org/pypi/pa-ringbuffer

This way, your installation always stays up-to-date, even if you pull new
changes from the Github repository and if you switch between branches.

If you prefer, you can also replace the last command with::

   python3 -m pip install --user -e .

... where ``-e`` stands for ``--editable``.

In both cases you can drop the ``--user`` flag if you want a system-wide
installation (assuming you have the necessary rights).
