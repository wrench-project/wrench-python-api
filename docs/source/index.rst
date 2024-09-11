
|build-badge| |license-badge|


Support
=======

The source code for this WRENCH's Python API package is available on
`GitHub <http://github.com/wrench-project/wrench-api>`_.

The WRENCH API (version 0.1) is functional but only covers subsets of the
WRENCH C++ Workflow and Action APIs.

See the examples in the `examples` directory with descriptions and explanations in `examples/README`. 

WRENCH version 2.3 is required, and the `wrench-daemon` target must have been built when installing (i.e., `make wrench-daemon; sudo make install`).

Our preferred channel to report a bug or request a feature is via WRENCH's Python
API Github `Issues Track <https://github.com/wrench-project/wrench-api/issues>`_.

You can also reach the WRENCH team via our support email:
support@wrench-project.org.

.. toctree::
    :caption: API Reference
    :maxdepth: 1

    api_simulation.rst
    api_file.rst
    api_workflow.rst
    api_task.rst
    api_standard_job.rst
    api_compound_job.rst
    api_action.rst
    api_sleep_action.rst
    api_compute_action.rst
    api_file_read_action.rst
    api_file_write_action.rst
    api_file_copy_action.rst
    api_file_delete_action.rst
    api_compute_service.rst
    api_bare_metal_compute_service.rst
    api_cloud_compute_service.rst
    api_virtual_machine.rst
    api_storage_service.rst
    api_file_registry_service.rst


.. |build-badge| image:: https://github.com/wrench-project/wrench-api/workflows/Build/badge.svg
    :target: https://github.com/wrench-project/wrench-api/actions
.. |license-badge| image:: https://img.shields.io/badge/License-LGPL%20v3-blue.svg
    :target: https://github.com/wrench-project/wrench-api/blob/main/LICENSE
