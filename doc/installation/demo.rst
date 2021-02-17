.. _demo:

===========
Demo set up
===========

There is a demo fixture that creates 4 different roles in the app. These roles have different combinations of the
following permissions:

* Can start destruction
* Can start review destruction
* Can view case details

From within the repository, the fixture can be loaded with:

    .. code:: shell

        python src/manage.py loaddata src/rma/fixtures/demo_data.json

Enabling demo mode
------------------

The demo mode can be activated by setting the environment variable ``AVC_DEMO_MODE`` to ``True``.
By default ``AVC_DEMO_MODE=False``.

Configuring services
--------------------

The record-management app must be connected to an instance of Open-Zaak. This can be done through the admin.
Once in the admin, navigate to **Configuratie** > **Services** and then click on **Service toevoegen**.

3 different services need to be configured in order to access the Zaken API, Catalogi API  and the Documenten API.

* The **API type** should be ``ZRC (Zaken)``.
* The **API root** could be ``http://example.com/zaken/api/v1/``.
* The **Authorization type** should be ``ZGW client_id + secret``.
* The credential to be filled are then **Client ID** and **Secret**. These values are then needed later to configure access in OpenZaak!
* The **OAS** could be ``http://example.com/zaken/api/v1/schema/openapi.json``.


Configuring OpenZaak
--------------------

In the OpenZaak admin, navigate to **API Autorisaties** > **Applicaties** and click on **Applicatie toevoegen**.
Fill in the form:

* The **Label** should be ``Archiefvernietigingscomponent``
* The **Client ID** and the **Secret** should be those configured earlier in the Archiefvernietigingscomponent.



