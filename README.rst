Onion Omega Logging Server
==========================

Bottle.py based server application logging messages from devices in Omega's local
network into a JSON file. This application assumes that you are using a Omega2 and
have a microSD card inserted extending the ``/overlays`` path. It also includes a
HTML based overview and management page for configuration, data download and device
management. That page is still under construction.

Roadmap
-------

The next steps to be implemented are:

- RESTful endpoints for device management
- device overview on the dashboard
- show last logs on dashboard
- Substitute / Add a database approach for saving logs
- download options
- integrate CRONs for passing data (aggregates) to a remote server
- implement handlers for aggregating data, that shall be passed to a remote server
- implement GSM (for connecting to remote server)
- implement TTN (for connecting to remote server)
- add a linux service file & setup script

Install
-------

``omega-logserver`` is based on `bottle.py <https://bottlepy.org>`_, which is as of now
the only requirement.
After downloading the source files, the ``config.json.default`` has to be copied
to a new file called ``config.json`` and you need to place your configuration there.
Alternatively, you can download the latest release on Github, where this file is already
created.

.. warning::

    In case you want to update an existing project, do not downlaod the release as this
    will overwrite your configuration. Make a ``git pull`` instead.

Using the source files, log into you Omega and open the console (or ssh everything).
In case python3 and git are not installed yet:

.. code-block:: opkg

    opkg install python3-light
    opkg install git
    opkg install git-http
    opkg install ca-bundle

Clone the repo:

.. code-block:: bash

    git clone https://github.com/kit-hyd/omega-logserver.git
    cd omega-logserver
    pip install -r requirements.txt
    cp config.json.default config.json

And then start the server:

.. code-block:: bash

    cd omega-logserver
    python3 logserver.py

Now you can point a browser to the Onion. The address is depending on the configuration
in the ``config.json``. The default ``host_ip`` is ``192.168.3.1``. This is the
IP of the onion omega in its own AP network. Therefore you will have to log into the
Omega network and point a browser to ``http://192.168.3.1:5555``. In case your
omega is also connected to your home network, you can change the setting to the
local address of that network, this is however not recommended as there is no
security layer implemented into this package.

Service
-------

There is also an ``procd`` file in the repository. That file can be copied to
``/etc/init.d/logserver`` to create a ``logserver`` service.

.. code-block:: bash

    cd omega-logserver
    cp logserver /etc/init.d/logserver
    chmod +x /etc/init.d/logserver

Now, you can manually start and stop the logserver

.. code-block:: bash

    service logserver start
    service logserver stop

If you want the logserver to automatically start at system startup, you can enable
the service

.. code-block:: bash

    service logserver enable

This will start the service on next system boot.


.. important::

    The procd service assumes that you are using the python3 interpreter and
    have the repository at ``/root/omega-logserver/``. In case you change this
    location, you'll have to adjust the service file.