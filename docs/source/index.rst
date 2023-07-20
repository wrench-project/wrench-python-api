
|build-badge| |license-badge|


Support
=======

The source code for this WRENCH's Python API package is available on
`GitHub <http://github.com/wrench-project/wrench-api>`_.

The WRENCH API (version 0.1) is functional but pretty experimental at this stage. 
See the example in `example/simulator.py`. Note that WRENCH version 2.2 is required, as
it includes the `wrench-daemon` which must be started on the local machine before
executing a WRENCH Python program, like the above example. 


Our preferred channel to report a bug or request a feature is via WRENCH's Python
API Github `Issues Track <https://github.com/wrench-project/wrench-api/issues>`_.

You can also reach the WRENCH team via our support email:
support@wrench-project.org.

.. toctree::
    :caption: API Reference
    :maxdepth: 1

    api_simulation.rst
    api_simulation_item.rst
    api_file.rst
    api_compute_service.rst
    api_bare_metal_compute_service.rst
    api_cloud_compute_service.rst
    api_virtual_machine.rst
    api_storage_service.rst
    api_standard_job.rst
    api_task.rst

.. |build-badge| image:: https://github.com/wrench-project/wrench-api/workflows/Build/badge.svg
    :target: https://github.com/wrench-project/wrench-api/actions
.. |license-badge| image:: https://img.shields.io/badge/License-LGPL%20v3-blue.svg
    :target: https://github.com/wrench-project/wrench-api/blob/main/LICENSE
