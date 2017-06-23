Vagrant Setup for HAWC
======================

Information for setting up HAWC using the included VagrantFile. Requirements
include `Vagrant <https://www.vagrantup.com/>`_ and a VM provider, such as
`VirtualBox <https://www.virtualbox.org/wiki/VirtualBox>`_.

The included VagrantFile sets up a VM with the following features:

* Ubuntu 16.04 (Xenial Xerus)
* 2GB of RAM
* Forwarded ports:
** Port 3000 > 3000 (Node server for JavaScript)
** Port 8000 > 8000 (Django server for Python)
** Port 80 > 8081 (If you want to use Nginx)
** Port 5432 > 5432 (PostgreSQL access)
** If the port is already used on the host system, Vagrant will choose another.

Project Setup
~~~~~~~~~~~~~

#. Go to your projects folder
#. :command:`git clone https://github.com/teamhero/hawc.git`
#. :command:`cd hawc`

Starting Vagrant
~~~~~~~~~~~~~~~~

#. :command:`vagrant up`
#. :command:`vagrant ssh`

Server Setup
~~~~~~~~~~~~

Redis
-----

#. :command:`sudo apt-get -y install redis-server`

PostgreSQL 9.6
--------------

#. :command:`sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ \`lsb_release -cs\`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'`
#. :command:`wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -`
#. :command:`sudo apt-get update && sudo apt-get -y install postgresql postgresql-contrib postgresql-server-dev-9.6`
#. :command:`sudo su - postgres`
#. :command:`createdb -E UTF-8 hawc`
#. :command:`psql`
#. :command:`alter user postgres with password 'password';`
#. :command:`\\q`
#. :command:`exit`
#. :command:`sudo nano /etc/postgresql/9.6/main/pg_hba.conf`
#. Replace ``peer`` with ``md5`` on the two lines that start with ``local``
#. :command:`Ctrl-X`, then :command:`Ctrl-Y`, then :command:`Enter`
#. :command:`sudo nano /etc/postgresql/9.6/main/postgresql.conf`
#. Change ``#listen_addresses = 'localhost'`` to ``listen_addresses = '*'``
#. :command:`Ctrl-X`, then :command:`Ctrl-Y`, then :command:`Enter`
#. :command:`sudo service postgresql restart`
