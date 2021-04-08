.. _faq:

Frequently asked questions
==========================

What exactly is deleted by the application?
----------------------------------------------

The application is an interface on top of the `API's voor Zaakgericht Werken`_,
as present in for example `Open Zaak`_. If the application has the proper 
authorizations for the APIs and a destruction list with cases (zaken) is 
approved, the application will delete:

* The cases in the `Zaken API`_ and all related objects within the same API, 
  including the audit trail.
* All documents (documenten) in the `Documenten API`_, related to the deleted 
  case if the document is not related to any other case. All related objects to 
  the document within the same API are also deleted. If the document is related 
  to another case, only the relation to the deleted case, is deleted.
* All decisions (besluiten) in the `Besluiten API`_, related to the deleted 
  case. All related objects to the decision within the same API are also 
  deleted.

Are things really deleted?
--------------------------

Yes! Deleting or destroying cases (zaken) will remove the record from the 
database. It's not just a flag that is set on the deleted case.

I accidentally deleted a case, can I get it back?
-------------------------------------------------

No! Unless you have a backup of the data, you cannot undo a deletion or get the
data back.

Is related data, not part of the `API's voor Zaakgericht Werken`_, deleted?
------------------------------------------------------------------------

The application destroys cases and related documents and decisions in the 
`API's voor Zaakgericht Werken`_. The application has no direct control over
data that is stored in other applications, registers, APIs or components.

It's the responsibility of the record manager or archivist to make sure that 
data, related to the case that is deleted, is also deleted.

There are some technical considerations that can be made to delete related data
automatically when the case is deleted.

See: :ref:`integration`

.. _`API's voor Zaakgericht Werken`: https://github.com/VNG-Realisatie/gemma-zaken
.. _`Open Zaak`: https://opengem.nl/producten/open-zaak/
.. _`Zaken API`: https://vng-realisatie.github.io/gemma-zaken/standaard/zaken/index
.. _`Besluiten API`: https://vng-realisatie.github.io/gemma-zaken/standaard/besluiten/index
.. _`Documenten API`: https://vng-realisatie.github.io/gemma-zaken/standaard/documenten/index
