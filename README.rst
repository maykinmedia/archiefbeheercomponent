=============================
Archiefvernietigingscomponent
=============================

:Version: 0.1.0
:Source: https://github.com/maykinmedia/archiefvernietigingscomponent
:Keywords: Common Ground, Record Management, Archiving

|build-status| |code-quality| |black| |python-versions|

Create, manage and execute destruction lists, for use with for "Zaakgericht 
werken" (case-oriented working).
(`Nederlandse versie`_)

Developed by `Maykin Media B.V.`_ commissioned by the Municipality of Utrecht and Delft.


Introduction
============

Record management is the practice of destroying data-records that have met their
end-of-life time. "Zaakgericht werken" prescribes the archiving terms for cases 
that have been brought to an end.

The Archiefvernietigingscomponent (AVC) provides functionality for record 
managers to schedule destruction of cases according to the archiving parameters.
It implements a multi-step, multi-role accordance process.

Attention is paid to the user experience of the staff using the app, with 
notifications to inform you of pending work-load, full audit logging and 
traceability of user and system actions.

The AVC supports all backends implementing the 1.0.x 
`API's voor Zaakgericht Werken`_, like `Open Zaak`_.

Quickstart
==========

A `docker-compose-quickstart.yml`_ is provided to get up and running quickly. To run the container:

    .. code:: shell

        $ wget https://raw.githubusercontent.com/maykinmedia/archiefvernietigingscomponent/master/docker-compose-quickstart.yml
        $ docker-compose -f docker-compose-quickstart.yml up -d
        $ docker-compose exec web src/manage.py createsuperuser

Then, navigate to ``http://127.0.0.1:8000/`` and log in with the credentials created.

.. _docker-compose-quickstart.yml: docker-compose-quickstart.yml

Documentation
=============

See ``INSTALL.rst`` for installation instructions, available settings and
commands.

License
=======

Copyright © Maykin Media, 2021

Licensed under the `EUPL`_.

References
==========

* `Issues <https://github.com/maykinmedia/archiefvernietigingscomponent/issues>`_
* `Code <https://github.com/maykinmedia/archiefvernietigingscomponent>`_
* `Community <https://commonground.nl/groups/view/54478547/archiefbeheercomponent>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/archiefvernietigingscomponent>`_

.. _`Nederlandse versie`: README.NL.rst
.. _`Maykin Media B.V.`: https://www.maykinmedia.nl
.. _`API's voor Zaakgericht Werken`: https://github.com/VNG-Realisatie/gemma-zaken
.. _`Open Zaak`: https://opengem.nl/producten/open-zaak/
.. _`Common Ground`: https://commonground.nl/
.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/maykinmedia/archiefvernietigingscomponent/workflows/Run%20CI/badge.svg?branch=master
    :alt: Build status
    :target: https://github.com/maykinmedia/archiefvernietigingscomponent/actions?query=branch%3Amaster+workflow%3A%22Run+CI%22

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |python-versions| image:: https://img.shields.io/badge/python-3.8-blue.svg
    :alt: Supported Python version

.. |code-quality| image:: https://github.com/maykinmedia/archiefvernietigingscomponent/workflows/Code%20quality%20checks/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/archiefvernietigingscomponent/actions?query=workflow%3A%22Code+quality+checks%22
