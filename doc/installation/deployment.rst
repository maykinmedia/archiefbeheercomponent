.. _deployment:

==========
Deployment
==========

Deployment is done via `Ansible`_. Currently, only single server deployments
are described but you can just as easily deploy the application in a Kubernetes
environment.

.. warning:: The deployment configuration (called a "playbook") is very 
   simplistic and also contains sensitive values. This makes the playbook more 
   readable but is not following good practices!

1. Download the project from Github or just the `deployment files`_.

   .. code:: shell

      $ git clone git@github.com:maykinmedia/archiefvernietigingscomponent.git

2. Setup virtual environment:

   .. code:: shell

      $ python3 -m venv env/
      $ source env/bin/activate
      $ pip install ansible

   .. note:: Sometimes, additional or updates packages are needed if they 
      are not installed by the Ansible setup installation. You can do so like 
      this:

      .. code:: shell

         $ python -m pip install -U pip
         $ pip install ordered_set packaging appdirs six

3. Install Ansible collections:

   .. code:: shell

      $ ansible-galaxy collection install git+https://github.com/maykinmedia/commonground-ansible.git

   .. note:: This collection might require explicit access.

4. Edit the playbook ``app.yml`` to match your setup. Take special note of all
   **TODO** settings and **read through all the comments**.

5. Run the playbook:

   .. code:: shell

      $ ansible-playbook app.yml --become --ask-become-pass


.. _`Ansible`: https://www.ansible.com/
.. _`deployment files`: https://github.com/maykinmedia/archiefvernietigingscomponent/tree/master/deployment