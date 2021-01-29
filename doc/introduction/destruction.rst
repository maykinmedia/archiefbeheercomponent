.. _destruction:

===================
Destruction process
===================

The destruction process takes care of destroying the case data, with respect to their
archiving law parameters.

As part of "zaakgericht werken" ("case management"), the archive parameters are
determined during the life-cycle of a case. There are two possible actions:

- destroy cases
- keep cases (and transfer them to an e-depot)

Each case has an "archive action date", which is the date after wich the determined
action needs to be performed.

The derivation of these parameters is part of the standard for
"API's voor Zaakgericht Werken". The Archiefvernietigingscomponent provides the tooling to perform the destruction
of the cases past the archive action date.

.. note:: When we mention destruction, we mean permanent destruction. The API calls made
   to the involved API's cause the data to be erased from the database and documents to
   be removed from the file systems.

The next sections document the process as implemented in the Archiefvernietigingscomponent.

Destruction list creation
=========================

A user with sufficient permissions (see :ref:`configuraton_permissions`) can bring up
the destruction list creation screen.

Filters are provided on the left hand side, while the main content shows a table of
cases matching the filter criteria. Only the cases that have their archive action date
before or on the current date are available.

Filters
-------

The filters allow you to select a sub-set of cases based on case-type. Each case type
displays the various versions, so you can limit the selection to a specific version.

You can also filter on start date - only cases started before or on the selected date
are retrieved.

Case selection
--------------

The destruction list author adds cases to the destruction list by checking the checkbox.
The checkbox in the table heading can be used to toggle *all* cases matching the
provided filters.

In the top-right, a summary of the amount of selected cases is displayed.

Finalizing the list creation
----------------------------

Once all relevant cases have been selected, the list author can now finalize the list
creation by clicking the top-right button, which brings up a form.

The form requires you to give the list a name for identification purposes, and you
specify which users should be involved in the review process. The reviewers should be
selected in order of review.

Available users are selected based on their role permission.

Once the confirmation button is clicked, the list is created and assigned to the first
reviewer.

Destruction list review
=======================

Each reviewer assigned to a list performs the review in turn after the previous reviewer
has approved the destruction list.

Each reviewer has the option to suggest exemptions or changes:

- exemptions: suggests removing the case from the destruction list
- changes: the reviewer can provide a comment so that the author knows which changes to
  make to the archiving parameters. The case will also be removed from the list

Once a reviewer suggests changes or exemptions, the original list author is assigned,
where they process the changes. After processing the changes, the review flow restarts
with the first reviewer.

After the last reviewer has given their approval, the list is submitted for actual
destruction to the background worker queue.

Audit trails and logs
=====================

Destruction list assignees receive notifications when important events happen, such as
being the next assignee on the list.

Additionally, audit trails are collected for list creation, review submission and case
deletion (for every individual case!).
