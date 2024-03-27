==============
Change history
==============

1.1.4
=====

*March 27th, 2024*

* Fixed the `DEFAULT_FROM_EMAIL` setting not using the environment variable.
* Fixed incompatibilities with Open Zaak in the `create-demo-data` management command

1.1.1
=====

*February 7th, 2023*

* Upgrade Python / JavaScript dependencies reported by dependabot alerts

1.1.0
=====

*June 24, 2022*

* [#236] Fixed the 500 error happening when a user was created through the admin.
* [#244] Improved management command to generate demo data. Now if the demo catalog already exists, no error is raised.
* [#79] Updated the record manager destruction list view so that it only has the buttons "suggest changes" and
   "approved". Updated the process owner destruction list view so that it only has the buttons "exclude case" and "keep case".
* [#247] Added the possibility of automatically sending an email reminder to a reviewer that still hasn't reviewed a destruction list after a period of time.
* [#91] Added configuration to specify after how long the email reminder should be sent to reviewers.
* [#91] Highlight in the record manager list view which destruction lists for which a reminder has been sent to the reviewer.
* [#91] Added ability to cancel destruction lists that have not been reviewed yet.
* [#91] Added email template for the automatic email reminder to be sent to the reviewers.
* [#155] / [#261] Added the possibility to automatically create a case containing the destruction report after a destruction list has been processed.
   Downloading the destruction report through the application is now configurable.
* [#53] / [#268] Added a view where a record manager can look at closed cases without archiving date. For this to be possible, additional filters had to be added to Open-Zaak.
* [#54] / [#240] / [#264] From the view with closed cases without archive date, it is possible to update the archiving
   information of the case. Any errors raised from Open-Zaak are shown to the record manager.
* [#254] Added search field on case identification to the view with closed cases without archive date.
* [#263] The 'Opstellen' page and the 'Zaken zonder archiefactiedatum' page now have some text explaining exactly which cases are displayed.
* [#262] Added a management command ``configure-types`` to add demo zaaktype/informatieobjecttype/statustype/resultaattype to Open-Zaak for the case that gets created once a destruction list is processed.
* [#239] From the  view where a record manager can look at closed cases without archiving date, it is now possible to select cases and export them as an excel file.
* [#241] Changed the name of the application from ``Archiefvernietigingscomponent`` to ``Archiefbeheercomponent``
* [#87] Handle "zaak not found" errors when already-processed destruction list are displayed in a view.
* [#227] Disable buttons in reviewers views while the page is loading.
* [#215] Removed startdatum filter from the 'Opstellen' page.
* [#252] Refactor of the frontend to use immer where too many ``useState`` calls were used. Added React error boundaries.
* [#256] / [#301] Updated translation files.
* [#216] Made the logo into a link to the home page, so that its easier to navigate in the application.
* [#290] Improvements to the column headers in the record manager and reviewers views.
* [#291] Show in the destruction report how many MBs of documents have been deleting while processing a destruction list.
* [#295] Added missing query parameter in the download link for the destruction report sent in the email to the archivist.
* [#288] Added the possibility to upload documents while reviewing a destruction list. This then gets added to the zaak which is created after the destruction list is processed.
* [#287] Show a notification once a destruction list has been processed and a case has been created. The notification shows the identification of the case created.
* [#297] Improve styling of error messages.

In addition, both python and JS dependencies were bumped based on the dependabot alerts.

1.0.0
=====

*April 25, 2021*

* Initial release of the Archiefvernietigingscomponent!

0.1.0
=====

*July 21, 2020*

This is an unreleased version to mark the last commit done by the municipality
of Utrecht before their "Record Management App" was picked up by the
municipality of Delft to evolve the application to the
"Archiefvernietigingscomponent" in several Common Ground sprints.
