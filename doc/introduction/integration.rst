.. _integration:

=======================================
Integration tips for software suppliers
=======================================

The ArchiefBeheerComponent destroys cases, related documents and
decisions in the `API's voor Zaakgericht Werken`_. The application has no
direct control over data that is stored in other applications, registers, APIs
or components.

It's the responsibility of the record manager or archivist to make sure that
data, related to the case that is deleted, is also deleted. There are some
technical considerations that can be made to delete related data automatically
when the case is deleted.

Software suppliers can make use of the implementation scenarios below to
facilitate the destruction proces in accordance with the Dutch law.

Implementation scenarios
========================

In all cases, your application needs to store the case identifier (URL or UUID)
that links the local data with the case in the `Zaken API`_ in order to match
them.

Subscribe to the Notificaties API
---------------------------------

When a case is deleted, a notification is sent to all subscribers by the
`Notificaties API`_. This behaviour is part of the
`API's voor Zaakgericht Werken`_ and not specific for the
ArchiefBeheerComponent.

Your application can listen to these notifications and delete its locally
stored data that is related to the case that is deleted.

Keep in mind that when you receive the notification, the case is already
deleted and it can no longer be retrieved from the Zaken API.

Keep track of the "archiefactiedatum"
-------------------------------------

Although this is not good `Common Ground`_ practice, your application can make
a copy of the ``archiefactiedatum`` of the case and store it with your local
data.

You can then schedule regular intervals to update your copy of the
``archiefactiedatum`` in case it changes and schedule a regular destruction
process to delete your local data according to the (locally kept)
``archiefactiedatum``.

This destruction process should check if the case is already deleted. Cases
are typically not deleted on, or right after, their ``archiefactiedatum`` and
local data should not be deleted before the case is deleted!

Keep track of deleted cases
---------------------------

A more simple version of the above but less efficient and more prone to issues.

Your application can check whether a case is deleted in the `Zaken API`_.
Although you cannot really check if a case is deleted, you can only check if the
case is not present (anymore) in the `Zaken API`_.

This might be a trigger to delete your local data as well. You should however
be very careful with situations where there is another reason why you cannot
retrieve a case from the `Zaken API`_ anymore (authorizations, network issues,
URL changes, etc.)


Storing local/domain data in an (third party) API
=================================================

If your application stores data in an (third party) API, like the
`Objects API`_, it is still the responsibility of your application to delete
the objects in such an API. The object needs to have (and thus store) a
relation to the case in order to match it to the deleted case.

You can then use one of the implementation scenarios to perform the deletion.


.. _`API's voor Zaakgericht Werken`: https://github.com/VNG-Realisatie/gemma-zaken
.. _`Open Zaak`: https://opengem.nl/producten/open-zaak/
.. _`Objects API`: https://opengem.nl/producten/overige-registraties/
.. _`Common Ground`: https://commonground.nl/
.. _`Zaken API`: https://vng-realisatie.github.io/gemma-zaken/standaard/zaken/index
.. _`Notificaties API`: https://vng-realisatie.github.io/gemma-zaken/standaard/notificaties/index
