Contributing
============

Restructured text is the markup language used for documentation. Helpful links
for learning more about the syntax and features are found here:

- `Quick guide`_
- `Live editing`_

.. _`Quick guide`: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _`Live editing`: http://rst.ninjs.org/


Developer environment settings
------------------------------

Here is an example folder-level configuration setting for vscode:

.. code-block:: json

    {
        "restructuredtext.linter.disabled": true,
        "[html]": {
            "editor.formatOnSave": false
        },
        "[python]": {
            "editor.formatOnSave": true
        },
        "[javascript]": {
            "editor.formatOnSave": false,
            "editor.codeActionsOnSave": {
                "source.fixAll.eslint": true
            }
        },
        "editor.formatOnSave": true,
        "python.pythonPath": "./venv/bin/python",
        "python.linting.flake8Args": [
            "--config=.flake8"
        ],
        "eslint.workingDirectories": [
            "./frontend"
        ]
    }
