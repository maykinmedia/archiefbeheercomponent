=============================
Archiefvernietigingscomponent
=============================

:Version: 0.1.0
:Source: https://github.com/maykinmedia/archiefvernietigingscomponent
:Keywords: Common Ground, Record Management, Archiveren

|build-status| |code-quality| |black| |python-versions|

Opstellen, beheren en uitvoeren van vernietigingslijsten, voor gebruik met 
Zaakgericht werken.
(`English version`_)

Ontwikkeld door `Maykin Media B.V.`_ voor de Gemeente Utrecht en Delft.


Introductie
===========

Archiefbeheer draait om het vernietigen van gegevens die aan het einde van hun 
levensduur zijn gekomen. Zaakgericht werken schrijft de archiveringsvoorwaarden 
voor, voor zaken die zijn beëindigd.

De Archiefvernietigingscomponent (AVC) biedt functionaliteit voor archiefbeheer 
om de vernietiging van zaken in te plannen volgens de archiveringsvoorwaarden. 
De AVC volgt een proces dat uit meerdere stappen bestaat, over verschillende 
rollen.

Er is aandacht besteed aan de gebruikerservaring van de beheerders die de app 
gebruiken, met notificaties om te informeren over lopende taken, volledige 
auditregistratie en traceerbaarheid van gebruiker- en systeemacties.

De AVC ondersteunt alle backends die de 1.0.x `API's voor Zaakgericht Werken`_ 
implementeren, zoals `Open Zaak`_.

Quickstart
==========

Om het startprocess van de Archiefvernietigingscomponent te vereenvoudigen, is er een `docker-compose-quickstart.yml`_ beschikbaar.
Voer de volgende commando's uit om de containers te starten:

    .. code:: shell

        $ wget https://raw.githubusercontent.com/maykinmedia/archiefvernietigingscomponent/master/docker-compose-quickstart.yml
        $ docker-compose -f docker-compose-quickstart.yml up -d
        $ docker-compose exec web src/manage.py createsuperuser

Ga daarna naar ``http://127.0.0.1:8000/`` en log in met de inloggegevens die je zojuist hebt gemaakt.

.. _docker-compose-quickstart.yml: docker-compose-quickstart.yml

Documentatie
============

Instructies voor de installatie en configuratie vindt u in ``INSTALL.rst``.

Licentie
========

Copyright © Maykin Media, 2021

Licensed under the `EUPL`_.

Referenties
===========

* `Issues <https://github.com/maykinmedia/archiefvernietigingscomponent/issues>`_
* `Code <https://github.com/maykinmedia/archiefvernietigingscomponent>`_
* `Community <https://commonground.nl/groups/view/54478547/archiefbeheercomponent>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/archiefvernietigingscomponent>`_

.. _`English version`: README.rst
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
