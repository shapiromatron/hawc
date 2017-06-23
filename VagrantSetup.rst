Vagrant Setup for HAWC
======================

Information for setting up HAWC using the included VagrantFile. Requirements
include `Vagrant <https://www.vagrantup.com/>`_ and a VM provider, such as
`VirtualBox <https://www.virtualbox.org/wiki/VirtualBox>`_.

The included VagrantFile sets up a VM with the following features:

* Ubuntu 16.04 (Xenial Xerus)
* 2GB of RAM
* Forwarded ports:

  * Port 3000 > 3000 (Node server for JavaScript)
  * Port 8000 > 8000 (Django server for Python)
  * Port 80 > 8081 (If you want to use Nginx)
  * Port 5432 > 5432 (PostgreSQL access)
  * If the port is already used on the host system, Vagrant will choose another.

Project Setup
~~~~~~~~~~~~~

#. Go to your projects folder
#. git clone https://github.com/teamhero/hawc.git
#. cd hawc

Starting Vagrant
~~~~~~~~~~~~~~~~

#. vagrant up
#. vagrant ssh

Server Setup
~~~~~~~~~~~~

Redis
-----

#. sudo apt-get -y install redis-server

PostgreSQL 9.6
--------------

#. sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ \`lsb_release -cs\`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
#. wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
#. sudo apt-get update && sudo apt-get -y install postgresql postgresql-contrib postgresql-server-dev-9.6
#. sudo su - postgres
#. createdb -E UTF-8 hawc
#. psql
#. alter user postgres with password 'password';
#. \\q
#. exit
#. sudo nano /etc/postgresql/9.6/main/pg_hba.conf
#. Replace ``peer`` with ``md5`` on the two lines that start with ``local``
#. Ctrl-X, then Ctrl-Y, then Enter
#. sudo nano /etc/postgresql/9.6/main/postgresql.conf
#. Change ``#listen_addresses = 'localhost'`` to ``listen_addresses = '*'``
#. Ctrl-X, then Ctrl-Y, then Enter
#. sudo service postgresql restart
