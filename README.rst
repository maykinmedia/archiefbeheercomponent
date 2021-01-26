=====================
Record Management App
=====================

:Version: 0.1.0
:Source: https://github.com/GemeenteUtrecht/record-management-app
:Keywords: Common Ground, Record Management, Archiveren
:PythonVersion: 3.8

Zaakgericht record-management in het Common Ground landschap.

Ontwikkeld door `Maykin Media B.V.`_ voor Gemeente Utrecht.


Introduction
============

Record management is the practice of destroying data-records that have met their
end-of-life time. "Zaakgericht werken" prescribes the archiving terms for cases that
have been brought to an end.

The RMA provides functionality for record managers to schedule destruction of cases
according to the archiving parameters. It implements a multi-step, multi-role accordance
process.

Attention is paid to the user experience of the staff using the app, with notifications
to inform you of pending work-load, full audit logging and traceability of user and
system actions.

The RMA supports all backends implementing the 1.0.x `API's voor Zaakgericht Werken`_.

Quickstart
==========

A `docker-compose-quickstart.yml`_ is provided to get up and running quickly. To run the container:

    .. code:: shell

        $ wget https://raw.githubusercontent.com/maykinmedia/record-management-app/master/docker-compose-quickstart.yml
        $ docker-compose -f docker-compose-quickstart.yml up -d
        $ docker-compose exec web src/manage.py createsuperuser

Then, navigate to ``http://127.0.0.1:8000/`` and log in with the credentials created.

.. _docker-compose-quickstart.yml: docker-compose-quickstart.yml

Documentation
=============

See ``INSTALL.rst`` for installation instructions, available settings and
commands.


References
==========

* `Issues <https://github.com/GemeenteUtrecht/record-management-app/issues>`_
* `Code <https://github.com/GemeenteUtrecht/record-management-app>`_

.. _Maykin Media B.V.: https://www.maykinmedia.nl
.. _API's voor Zaakgericht Werken: https://github.com/VNG-Realisatie/gemma-zaken
