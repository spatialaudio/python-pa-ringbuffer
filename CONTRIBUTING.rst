Contributing
------------

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
https://github.com/spatialaudio/python-pa-ringbuffer/.
Contributions are always welcome!

Instead of pip-installing the latest release from PyPI_, you should get the
newest development version (a.k.a. "master") with Git::

   git clone https://github.com/spatialaudio/python-pa-ringbuffer.git
   cd python-pa-ringbuffer
   python3 -m pip install -e . --user

... where ``-e`` stands for ``--editable``.

When installing this way, you can quickly try other Git
branches (in this example the branch is called "another-branch")::

   git checkout another-branch

If you want to go back to the "master" branch, use::

   git checkout master

To get the latest changes from Github, use::

   git pull --ff-only

.. _PyPI: https://pypi.python.org/pypi/pa-ringbuffer
