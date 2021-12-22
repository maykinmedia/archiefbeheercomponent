.. _demo:

=========
Demo mode
=========

The demo mode is meant to guide you through the application, following a
predefined process with predefined roles.

.. warning:: Do not use this mode in production or any publicly accessible
   environment. In doing so, you might expose case data, documents, etc.

Prerequisites
-------------

You will need:

* A working ArchiefBeheerComponent, for example as installed via the :ref:`quickstart`,
* Full access to all `API's voor Zaakgericht werken`_, like an `Open Zaak`_ instance,
* Access to a Selectielijst API, like: https://selectielijst.openzaak.nl.

.. _`API's voor Zaakgericht Werken`: https://github.com/VNG-Realisatie/gemma-zaken
.. _`Open Zaak`: https://opengem.nl/producten/open-zaak/

.. note:: We assume you are using Open Zaak but this can be an component that
   offers the `API's voor Zaakgericht werken`_.

Setting up demo mode
--------------------

1. Enable demo mode.

   The demo mode can be activated by setting the environment variable
   ``ABC_DEMO_MODE`` to ``1``. By default ``ABC_DEMO_MODE=0``.

    .. tabs::

        .. group-tab:: Docker

            Change the `docker-compose.yml` file you are using to include the
            environment variable:

            .. code:: yaml

                  web:
                  image: maykinmedia/archiefbeheercomponent:latest
                  environment: &web_env
                     - ABC_DEMO_MODE=1
                     - DJANGO_SETTINGS_MODULE=archiefbeheercomponent.conf.docker
                     # etc...

            and stop and start the docker containers (do not just restart).

            .. code:: shell

                  $ docker-compose down
                  $ docker-compose up -d

        .. group-tab:: Python

            .. code:: shell

                  $ ABC_DEMO_MODE=1 python src/manage.py runserver


2. Navigate to ``http://127.0.0.1:8000`` and you will see that demo mode is
   enabled.

3. Click the red **Administration** button and login to start configuring the
   application.

4. For testing purposes we can fake the current date. Normally, only cases that
   should be destroyed today or earlier show up. If we set the date to 50 years
   in the future, most cases will show up.

   a. Navigate to **Configuratie > Archiveringsconfiguratie**

   b. Fill in the **Archiefdatum** to specify the fake "current date".

   c. Click **Opslaan**.


.. note:: When the record-management app is in demo mode, cases are not
   *actually* destroyed, i.e. they remain in OpenZaak and can be included in
   new destruction lists.


You can continue to :ref:`configure <configuration>` the application.

Optional destruction case
-------------------------

If the feature to create a zaak related to the destruction report is turned on, the environment needs to be configured
with the right URLs (see the :ref:`configuration <optional destruction case settings>` section for more details).

For the demo environment, there is a management command that will create the required zaaktype, informatieobjecttype,
statustype and resultaattype in Open-Zaak and print the URLs to the console. These can then be used for the
configuration in the admin page.

    .. tabs::

        .. group-tab:: Docker

           .. code:: shell

              $ docker-compose exec web src/manage.py configure-types

        .. group-tab:: Python

          .. code:: shell

              $ source env/bin/activate
              $ python src/manage.py configure-types
