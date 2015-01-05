Python bindings to the OpenStack Vdi API
===========================================

This is a client for OpenStack Vdi API. There's :doc:`a Python API
<api>` (the :mod:`vdiclient` module), and a :doc:`command-line script
<shell>` (installed as :program:`vdi`). Each implements the entire
OpenStack Vdi API.

You'll need credentials for an OpenStack cloud that implements the
Data Processing API, in order to use the vdi client.

You may want to read the `OpenStack Vdi Docs`__  -- the overview, at
least -- to get an idea of the concepts. By understanding the concepts
this library should make more sense.

 __ http://docs.openstack.org/developer/vdi/api/index.html

Contents:

.. toctree::
   :maxdepth: 2

   api

Contributing
============

Code is hosted in `review.o.o`_ and mirrored to `github`_ and `git.o.o`_ .
Submit bugs to the Vdi project on `launchpad`_ and to the Vdi client on
`launchpad_client`_. Submit code to the openstack/python-vdiclient project
using `gerrit`_.

.. _review.o.o: https://review.openstack.org
.. _github: https://github.com/openstack/python-vdiclient
.. _git.o.o: http://git.openstack.org/cgit/openstack/python-vdiclient
.. _launchpad: https://launchpad.net/vdi
.. _launchpad_client: https://launchpad.net/python-vdiclient
.. _gerrit: http://wiki.openstack.org/GerritWorkflow

