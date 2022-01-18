.. _roles:

=====
Roles
=====

Typically the ArchiefBeheerComponent has 3 roles but you can rename
these roles in the application or create roles with different permissions.

Record manager
--------------

* The record manager initiates the process to destroy cases and generates the list of destruction.
* Executes quality control over the list, checks if there are relations that can’t be disconnected when the file is destroyed and if there are cases on the list that can’t be destroyed because of an exemption due to the criteria mentioned in the ‘selectielijst’ (this is the archiving policy list with all the storage periods per zaaktype/process and allowed exemptions).
* Makes sure the destruction list is forwarded to the process owner.

Process owner
-------------

* As the owner of the information, checks if all the cases on the list can be destroyed. Asks the question: Is the file still needed for the current business operation?
* Exempts files that are still needed and gives the argumentation for that.
* Approves the list, so it can be forwarded (in exctracted form/proces verbaal) to the municipal archivist/supervisor. Or sends the list back to the record manager, if there are exceptions/exemptions.
* Approves (after the approval of the municipal archivist and the actual destruction) the proces verbaal.


Municipal archivist / supervisor
--------------------------------

* Checks the request/proces verbaal from the process owner.
* Rejects or gives approval for the destruction.

