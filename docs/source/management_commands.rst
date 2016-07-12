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

- ``build_d3_styles``: notes. Assemble all CSS styles used in d3 visualizations and create a new CSS file which can be inserted into static SVG files containing all the style information from external-style sheets. Used for statically generating svg visualizations with appropriate styles on server using Inkscape.

    Example usage::

        $ python manage.py build_d3_styles

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
