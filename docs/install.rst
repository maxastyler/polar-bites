Installation
============

:doc:`polar-bites<index>` is hosted on `github <https://github.com/maxastyler/polar-bites>`_,
and can probably be installed using your favourite package manager.

poetry
------

Add a requirement to the github link to the :code:`[tool.poetry.dependencies]` section in your ``pyproject.toml`` file. 

.. code-block:: toml
		
   [tool.poetry.dependencies]
   polar-bites = {git = "https://github.com/maxastyler/polar-bites.git"}

You can control which version you use by commit, or tag. See the `poetry docs <https://python-poetry.org/docs/dependency-specification/#git-dependencies>`_ for that.

Once you've put the dependency in your ``pyproject.toml`` file, update the poetry virtual environment:

.. code-block:: sh

   poetry update
