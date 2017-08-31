HAWC Database
=============

The HAWC database is a `PostgreSQL`_ database; it utilizes some PostgreSQL-specific feature such as `JSON fields`_ and `Array fields`_. Therefore, it may be possible to migrate the data to other database formats, but it wouldn't be a trivial exercise. The overall database schema is as follows (sections below break down the schema into more digestible components):

.. _`PostgreSQL`: https://www.postgresql.org/
.. _`JSON fields`: https://www.postgresql.org/docs/current/static/datatype-json.html
.. _`Array fields`: https://www.postgresql.org/docs/current/static/arrays.html

.. figure:: _static/hawc-schema.png
   :width: 1000
   :align: center
   :alt: HAWC data schema

   **Last updated: 2017-08-31**. The image is very large; please save/or open in another tab.


Study and risk of bias schema
-----------------------------
.. figure:: _static/hawc-study-schema.png
   :width: 1000
   :align: center
   :alt: HAWC study data schema

   **Last updated: 2017-08-31**. Study, literature, and risk-of bias schema. The image is very large; please save/or open in another tab.

Animal bioassay schema
----------------------
.. figure:: _static/hawc-animal-schema.png
   :width: 1000
   :align: center
   :alt: HAWC animal bioassay data schema

   **Last updated: 2017-08-31**. Animal bioassay and BMD schema. The image is very large; please save/or open in another tab.

Epidemiology schema
-------------------
.. figure:: _static/hawc-epi-schema.png
   :width: 1000
   :align: center
   :alt: HAWC epidemiology data schema

   **Last updated: 2017-08-31**. Epidemiology and epidemiological meta-analysis schema. The image is very large; please save/or open in another tab.

*In-vitro* data schema
----------------------
.. figure:: _static/hawc-invitro-schema.png
   :width: 1000
   :align: center
   :alt: HAWC invitro data schema

   **Last updated: 2017-08-31**. *In vitro* data schema. The image is very large; please save/or open in another tab.

Schema figure generation
------------------------

To generate these database schema diagrams:

.. code-block:: bash

    python manage.py graph_models \
        -a -g --pydot \
        -o ../docs/source/_static/hawc-schema.png

    python manage.py graph_models \
        lit study riskofbias \
        -g --pydot \
        -o ../docs/source/_static/hawc-study-schema.png

    python manage.py graph_models \
        animal bmd \
        -g --pydot \
        -o ../docs/source/_static/hawc-animal-schema.png

    python manage.py graph_models \
        epi epimeta \
        -g --pydot \
        -o ../docs/source/_static/hawc-epi-schema.png

    python manage.py graph_models \
        invitro \
        -g --pydot \
        -o ../docs/source/_static/hawc-invitro-schema.png
