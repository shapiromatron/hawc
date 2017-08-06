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

Once you do the setup below , the VM is set up for HAWC development. Do `Starting
Vagrant`_, and then skip to `Running Dev HAWC`_ to start the VM up in the future.  

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
#. Add two lines (Opens PostgreSQL to external editors)

   * host all all 0.0.0.0/0 md5
   * host all all ::/0 md5

#. Ctrl-X, then Ctrl-Y, then Enter
#. sudo nano /etc/postgresql/9.6/main/postgresql.conf
#. Change ``#listen_addresses = 'localhost'`` to ``listen_addresses = '*'``
#. Ctrl-X, then Ctrl-Y, then Enter
#. sudo service postgresql restart

Python 3.6
----------

#. sudo add-apt-repository ppa:jonathonf/python-3.6
#. sudo apt-get update && sudo apt-get -y install python3.6 python3.6-venv python3-tk

Git
---

#. sudo apt-get -y install git

Node 6
------

#. curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
#. sudo apt-get -y install nodejs

Yarn
----

#. curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
#. echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
#. sudo apt-get update && sudo apt-get -y install yarn

PhantomJS
---------

#. sudo apt-get update && sudo apt-get -y install build-essential chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev
#. cd ~
#. export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
#. wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2
#. sudo tar xvjf $PHANTOM_JS.tar.bz2
#. sudo mv $PHANTOM_JS /usr/local/share
#. sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
#. phantomjs --version


HAWC Setup
~~~~~~~~~~

Install Dependencies
--------------------

#. cd /vagrant
#. cp ./project/hawc/settings/local.example.py ./project/hawc/settings/local.py
#. python3.6 -m venv venv
#. source ./venv/bin/activate
#. $VIRTUAL_ENV/bin/pip install wheel
#. $VIRTUAL_ENV/bin/pip install -r ./requirements/dev.txt
#. Make a sandwich
#. cd project
#. yarn install
#. Eat the sandwich

Adjust Django
-------------

#. Add MEDIA_ROOT = 'media' to /vagrant/project/hawc/settings/local.py to point to the media folder

Running Dev HAWC
~~~~~~~~~~~~~~~~

Django Start
------------

#. cd /vagrant/project
#. python manage.py migrate
#. python manage.py createcachetable
#. python manage.py runserver 0.0.0.0:8000 (starts the Django development server)

NPM Start
---------

#. Open a new console
#. Go to the hawc directory
#. vagrant ssh
#. cd /vagrant/project
#. npm start (builds the JavaScript and starts a node server)

View Site
---------

#. http://localhost:8000/ on a host machine browser

Other Vagrant Commands
~~~~~~~~~~~~~~~~~~~~~~

Stop
----

#. Shuts down VM
#. Go to the hawc folder on your local machine in the console
#. vagrant halt

Destroy
-------

#. Will destroy your virtual machine. Do not use unless you want to start the setup over again.
#. Go to the hawc folder on your local machine in the console
#. vagrant destroy

Optional
~~~~~~~~

Nginx install
-------------

#. sudo apt-get -y install nginx