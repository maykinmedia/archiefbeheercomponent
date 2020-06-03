Apache + mod-wsgi configuration
===============================

An example Apache2 vhost configuration follows::

    WSGIDaemonProcess rma-<target> threads=5 maximum-requests=1000 user=<user> group=staff
    WSGIRestrictStdout Off

    <VirtualHost *:80>
        ServerName my.domain.name

        ErrorLog "/srv/sites/rma/log/apache2/error.log"
        CustomLog "/srv/sites/rma/log/apache2/access.log" common

        WSGIProcessGroup rma-<target>

        Alias /media "/srv/sites/rma/media/"
        Alias /static "/srv/sites/rma/static/"

        WSGIScriptAlias / "/srv/sites/rma/src/rma/wsgi/wsgi_<target>.py"
    </VirtualHost>


Nginx + uwsgi + supervisor configuration
========================================

Supervisor/uwsgi:
-----------------

.. code::

    [program:uwsgi-rma-<target>]
    user = <user>
    command = /srv/sites/rma/env/bin/uwsgi --socket 127.0.0.1:8001 --wsgi-file /srv/sites/rma/src/rma/wsgi/wsgi_<target>.py
    home = /srv/sites/rma/env
    master = true
    processes = 8
    harakiri = 600
    autostart = true
    autorestart = true
    stderr_logfile = /srv/sites/rma/log/uwsgi_err.log
    stdout_logfile = /srv/sites/rma/log/uwsgi_out.log
    stopsignal = QUIT

Nginx
-----

.. code::

    upstream django_rma_<target> {
      ip_hash;
      server 127.0.0.1:8001;
    }

    server {
      listen :80;
      server_name  my.domain.name;

      access_log /srv/sites/rma/log/nginx-access.log;
      error_log /srv/sites/rma/log/nginx-error.log;

      location /500.html {
        root /srv/sites/rma/src/rma/templates/;
      }
      error_page 500 502 503 504 /500.html;

      location /static/ {
        alias /srv/sites/rma/static/;
        expires 30d;
      }

      location /media/ {
        alias /srv/sites/rma/media/;
        expires 30d;
      }

      location / {
        uwsgi_pass django_rma_<target>;
      }
    }
