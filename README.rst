============
special_days
============

:author: Nico den Boer

special_days is a quite trivial command line application which serves the following purposes:

* Send daily emails with a list of upcoming special days; birthdays and national holidays.

* Most important: Demonstrate a basic usage of a number of Python libraries

If you are actually going to use it, you will need to understand a bit about relational databases.


Demonstrated
============

* Modify the main Python file so it will use the Python version you want

* Command line argument parsing with the `argparse`_ library

* Getting user input from the console during execution of a Python script

* Sending email from Python with the `email`_ library in the simple form or using TLS

* Working with the `SQLAlchemy`_  library

* Create a README.rst in `ReStructuredText format`_ for github.com which can be tested through `online REST test service`_


.. _`SQLAlchemy`: http://www.sqlalchemy.org
.. _`argparse`: http://docs.python.org/library/argparse.html
.. _`email`: http://docs.python.org/library/email.html
.. _`ReStructuredText format`: http://docutils.sourceforge.net/rst.html
.. _`online REST test service`: http://www.tele3.cz/jbar/rest/rest.html


Installation
============

This code is written for Python 2.7

After cloning this repository, run:
pip-2.7 install -r requirements.txt

This will make sure all required packages are installed e.g. dependencies are met.

Issue ./main.py -h to see self-explanatory help.
If you want help for a specific command, then use for example ./main.py add-user -h

Copy the project dir to your server and add a periodic call to main.py in your crontab.

Enter and update data from the console.


Todo
============

* Suggestions are welcome


Other than that
===============

I am currently looking for `freelance`_ Python and Django projects. We also provide training for Python and Django, both in `Holland`_ and the `Czech republic`_.

.. _`freelance`: http://www.denboer-ims.nl/freelance_programmer.html
.. _`Holland`: http://www.denboer-ims.nl/cursus_python.html
.. _`Czech republic`: http://www.nicodenboer.com/python-skoleni.html