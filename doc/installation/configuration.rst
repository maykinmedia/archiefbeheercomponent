.. _configuraton:

=============
Configuration
=============

.. note:: The configuration documentation is aimed at (functional) administrators.

The Archiefvernietingscomponent supports run-time configuration for maximum flexibility to make it fit your
environment. This does also mean that a fresh installation is empty and not useful
without any configuration.

The configuration interface is available on ``https://example.com/admin/``, where
``example.com`` should be replaced by your actual domain.

.. _configuraton_permissions:

Accounts, roles and permissions
===============================

Permissions
-----------

The Archiefvernietingscomponent has a simple permission system, consisting of the following permissions:

**can start destruction**

  Someone who can start destruction is allowed to create destruction lists. A person
  with this permission will see a list of their own destruction lists on their landing
  page, and a button to create a new list.

**can review destruction**

  Someone with this permission can be assigned as a reviewer for a destruction list.
  On their landing page, they see an overview of all the destruction lists where they
  were once assigned as a reviewer. They can suggest changes/exemptions on destruction
  lists back to the destruction list author.

**can view case details**

  Someone with this permission is allowed to view more details about a case. This could
  be part of the review process or destruction list creation process.

Roles
-----

Navigate to **Admin > Authentication and authorization > Roles** to manage roles. Roles
define a set of permissions. An application user can have one role.

Typical example roles would be:

- **record manager**:
    - *can start destruction*: yes
    - *can review destruction*: no
    - *can view case details*: yes

- **process owner**:
    - *can start destruction*: no
    - *can review destruction*: yes
    - *can view case details*: yes

- **archivars**:
    - *can start destruction*: no
    - *can review destruction*: yes
    - *can view case details*: no

You can create as many roles as you want and name them as you see fit.

Accounts
--------

Via **Admin > Authentication and authorization > Users** you can manage individual users
known to the system. You can perform administrative actions such as:

- assigning a role to a user
- filling out their name/e-mail address
- (re)setting their password

ADFS
----

The Archiefvernietingscomponent admin interface and frontend support logging in through ADFS-backed single sign
on (SSO).

ADFS 2012 and 2016, and Azure AD are supported. See the `ADFS config guides`_ for
documentation on how to configure ADFS itself.

The ADFS configuration can be found under **Admin > Configuration > ADFS Configuration**.

Services
========

The Archiefvernietingscomponent does not store, synchronize or copy case data. All data is retrieved through the
Zaken, Catalogi and Documenten API. As such, these services need to be configured.

Navigate to **Admin > Configuration > Service** and add the details for your
environment.

.. note:: Archiefvernietingscomponent supports multiple services of the same type.

Catalogi API
------------

The Archiefvernietingscomponent uses the Catalogi API to provide filter options based on "zaaktype".

Add a service of the type ``ZTC``, and make sure to fill out:

- ``API root URL``: the API base URL of the service.
- ``Extra configuration``: a JSON object with the main catalogue ID, e.g.:

  .. code-block:: json

    {"main_catalogus_uuid": "09a4ae7a-98a3-4178-9559-b22b76cad3db"}

- ``Client ID``: the client ID for your "application" that was registered with the
  Catalogi API-serving application.
- ``Secret``: the Secret for your "application" that was registered with the
  Catalogi API-serving application.
- ``Authorization type``: ZGW-client_id + secret
- ``OAS``: URL to the API schema, normally this is ``API root URL`` + ``schema/openapi.yaml``.
- ``NLX url``: optional NLX outway-URL if the service is to be consumed over the NLX
  network.

Zaken API
---------

The Zaken API is used to retrieve the zaken matching the archiving terms. They are the
objects that are eventually destroyed by this application.

Add a service of the type ``ZRC``. The configuration steps for the Catalogi API apply
here, with the exception of "Extra configuration" - this is not required.

Documenten API
--------------

Cases ("zaken") almost always have relations to documents. If the case is being
destroyed, documents related to it (and no other cases) also need to be destroyed. For
that purpose, the Archiefvernietingscomponent needs access to the Documents API.

Add a service of the type ``DRC``. The configuration steps for the Catalogi API apply
here, with the exception of "Extra configuration" - this is not required.

Required scopes
---------------

The Catalogi, Zaken and Documenten API enforce authorization checks. For the correct
functioning of the Archiefvernietingscomponent, it needs the following scopes:

**Zaken API**

  - ``zaken.lezen``: used to display detail information
  - ``zaken.geforceerd-bijwerken``: used to change archiving parameters for exemptions
  - ``zaken.verwijderen``: used to destroy selected cases

**Catalogi API**

  - ``catalogi.lezen``: used to fetch available case-types

**Documenten API**

  - ``documenten.lezen``: used to display case detail information
  - ``documenten.verwijderen``: used to destroy documents as part of the case destruction

**Besluiten API**

  - ``besluiten.lezen``: used to display case detail information
  - ``besluiten.verwijderen``: used to delete "besluiten" as part of the case destruction

Archive configuration
=====================

The Archiefvernietingscomponent only offers cases of which the archive action date has passed, to prevent
destruction of cases before their scheduled archiving. This is annoying for testing
purposes, so the Archiefvernietingscomponent supports specifying the "current date".

Navigate to **Admin > Configuration > Archive configuration** to specify the
"current date".


.. _ADFS config guides: https://django-auth-adfs.readthedocs.io/en/latest/config_guides.html
