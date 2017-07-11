Management commands
===================

Custom management commands can be used for commonly-required operations in
the HAWC assessment. A description of each command is detailed below:

MyUser Module Commands
----------------------

- ``create_user``: Creates a new HAWC user from the command-line; deprecated in favor of adding users from Django admin

- ``get_user``: Given a session-id, return the User associated with this session. Helpful in determining who through a 500 error and what they may have been working on.:

    Example usage::

        $ python manage.py get_user vtjjwq129gxduikmjsf6xyrupkay8uwc
        > Session found!
        > Full name: John Doe
        > Email: johhnyd@email.com


Utils module commands
---------------------

- ``clear_cache``: Completely clears all cache.

    Example usage::

        python manage.py clear_cache


Assessment module commands
--------------------------
- ``assessment_db_dump``: notes. Create a PostgreSQL SQL import file which will recreate the current data schema, as well as load all data for the selected assessment_id. Can be loaded

    Example usage::

        $ python manage.py assessment_db_dump 1 > /path/to/export.sql

    Can be loaded using the following commands::

        psql -d hawc -f /path/to/export.sql

- ``clean_text``: notes. Clean field to remove control characters or other non-UTF-8 characters which can typically be added when users copy and paste from PDF documents.

    Example usage::

        # outputs changes to Excel file
        python manage.py clean_text assessment baseendpoint name --test

        # modifies database
        python manage.py clean_text assessment baseendpoint name

- ``compile_webpack``: notes. Compile webpack for production. Call before ``collectstatic``.

    Example usage::

        $ python manage.py compile_webpack


- ``hawc_counts``: Recursively iterate through all django models, and calculate the total number of objects in each model. Useful for determining where new content is being added.

    Example usage::

        $ python manage.py hawc_counts
        > HAWC object outputs 2016-04-28 11:48:36.600116
        > myuser.models   HAWCUser    408
        > myuser.models   UserProfile 290
        > assessment.models   Assessment  212
        > ...

Additional commands
-------------------

- Database ER diagrams

To view the HAWC database schema, make sure the `django_extensions`_ package
is required, as well as `pydot2`_  (not pydot or graphviz). Then, run the following
django management command(s)::

    # create for all apps
    python manage.py graph_models -a -g --pydot -o hawc.png

    # create ER for single apps
    python manage.py graph_models -g --pydot -o utils.png utils
    python manage.py graph_models -g --pydot -o myuser.png myuser
    python manage.py graph_models -g --pydot -o assessment.png assessment
    python manage.py graph_models -g --pydot -o lit.png lit
    python manage.py graph_models -g --pydot -o study.png study
    python manage.py graph_models -g --pydot -o riskofbias.png riskofbias
    python manage.py graph_models -g --pydot -o mgmt.png mgmt
    python manage.py graph_models -g --pydot -o animal.png animal
    python manage.py graph_models -g --pydot -o epi.png epi
    python manage.py graph_models -g --pydot -o epimeta.png epimeta
    python manage.py graph_models -g --pydot -o invitro.png invitro
    python manage.py graph_models -g --pydot -o bmd.png bmd
    python manage.py graph_models -g --pydot -o summary.png summary
    python manage.py graph_models -g --pydot -o comments.png comments

.. _`django_extensions`: https://github.com/django-extensions/django-extensions
.. _`pydot2`: https://pypi.python.org/pypi/pydot2/1.0.33
