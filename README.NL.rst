======================
ArchiefBeheerComponent
======================

:Version: 1.1.4
:Source: https://github.com/maykinmedia/archiefbeheercomponent
:Keywords: Common Ground, Record Management, Archiveren

|build-status| |code-quality| |docs| |coverage| |black| |python-versions|

Opstellen, beheren en uitvoeren van vernietigingslijsten, voor gebruik met
Zaakgericht werken.
(`English version`_)

Ontwikkeld door `Maykin Media B.V.`_ voor de Gemeente Utrecht en Delft.


Introductie
===========

Archiefbeheer draait om het vernietigen van gegevens die aan het einde van hun
levensduur zijn gekomen. Zaakgericht werken schrijft de archiveringsvoorwaarden
voor, voor zaken die zijn beëindigd.

De ArchiefBeheerComponent (ABC) biedt functionaliteit voor archiefbeheer
om de vernietiging van zaken in te plannen volgens de archiveringsvoorwaarden.
De ABC volgt een proces dat uit meerdere stappen bestaat, over verschillende
rollen.

Er is aandacht besteed aan de gebruikerservaring van de beheerders die de app
gebruiken, met notificaties om te informeren over lopende taken, volledige
auditregistratie en traceerbaarheid van gebruiker- en systeemacties.

De ABC ondersteunt alle backends die de 1.0.x `API's voor Zaakgericht Werken`_
implementeren, zoals `Open Zaak`_.

Quickstart
==========

Om het startprocess van de ArchiefBeheerComponent te vereenvoudigen, is er een `docker-compose-quickstart.yml`_ beschikbaar.
Voer de volgende commando's uit om de containers te starten:

    .. code:: shell

        $ wget https://raw.githubusercontent.com/maykinmedia/archiefbeheercomponent/master/docker-compose-quickstart.yml
        $ docker-compose -f docker-compose-quickstart.yml up -d
        $ docker-compose -f docker-compose-quickstart.yml exec web src/manage.py createsuperuser

Ga daarna naar ``http://127.0.0.1:8000/`` en log in met de inloggegevens die je zojuist hebt gemaakt.

.. _docker-compose-quickstart.yml: docker-compose-quickstart.yml

Licentie
========

Copyright © Maykin Media, 2021

Licensed under the `EUPL`_.

Referenties
===========

* `Documentatie <https://archiefbeheercomponent.readthedocs.io/>`_
* `Issues <https://github.com/maykinmedia/archiefbeheercomponent/issues>`_
* `Code <https://github.com/maykinmedia/archiefbeheercomponent>`_
* `Community <https://commonground.nl/groups/view/54478547/archiefbeheercomponent>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/archiefbeheercomponent>`_

.. _`English version`: README.rst
.. _`Maykin Media B.V.`: https://www.maykinmedia.nl
.. _`API's voor Zaakgericht Werken`: https://github.com/VNG-Realisatie/gemma-zaken
.. _`Open Zaak`: https://opengem.nl/producten/open-zaak/
.. _`Common Ground`: https://commonground.nl/
.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/maykinmedia/archiefbeheercomponent/workflows/Run%20CI/badge.svg?branch=master
    :alt: Build status
    :target: https://github.com/maykinmedia/archiefbeheercomponent/actions?query=branch%3Amaster+workflow%3A%22Run+CI%22

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |python-versions| image:: https://img.shields.io/badge/python-3.8-blue.svg
    :alt: Supported Python version

.. |code-quality| image:: https://github.com/maykinmedia/archiefbeheercomponent/workflows/Code%20quality%20checks/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/archiefbeheercomponent/actions?query=workflow%3A%22Code+quality+checks%22

.. |docs| image:: https://readthedocs.org/projects/archiefbeheercomponent/badge/?version=latest
    :target: https://archiefbeheercomponent.readthedocs.io/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/github/maykinmedia/archiefbeheercomponent/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/maykinmedia/archiefbeheercomponent
