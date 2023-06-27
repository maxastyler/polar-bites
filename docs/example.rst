Examples
========

A list of things you might want to do with :doc:`polar-bites <index>`.

Loading MATLAB files
--------------------

The function :func:`polar_bites.mat.load_mat_to_dataframe` is used to extract a structure array from a given ``.mat`` file.
It takes the filename of the ``.mat`` file, and optionally the name of the variable to extract, and the list of columns to extract. If not given a name, it will extract the first variable from the file. The list of columns allows for selection/transformation of the data before it is loaded into a dataframe.

The Column
``````````
The :class:`Column<polar_bites.column.Column>` class helps to load columns from a MATLAB data file. It is meant to be used with :func:`load_mat_to_dataframe<polar_bites.mat.load_mat_to_dataframe>`. There are five attributes that can be declared in a column, but only ``names`` is necessary.

For usage: if we are given the structure array in matlab

.. list-table:: MATLAB structure array
   :widths: 25 25 25 25
   :header-rows: 1

   * - very_long_column_name
     - array_column
     - other_column
     - column_to_ignore
   * - 1
     - [3 4 5]
     - 3
     - nil
   * - 1
     - [10 20 23 45]
     - 3
     - nil

We would use the following list of columns to extract the data:

.. code-block:: python

   columns = [
      Column(
         name="very_long_column_name",
	 rename="shorter_column"
	),
      Column(
         name="array_column",
	 is_array=True
	),
      Column(
	 name="other_column",
	 as_type=int,
	 pre_transform=lambda x: x+1
      )
   ]

This would give a 3-column dataframe, with the column ``very_long_column_name``
renamed to ``shorter_column``, the ``array_column`` transformed to a list of floats, and
``other_column`` to be an integer, with its value increased by 1.

Nested Structs
``````````````
When loading MATLAB data with nested structs, the column names are flattened by joining them with underscores. So, if there is a struct with column ``column_1``, which has a child struct with columns ``c1``, and ``c2``, they would be accessible with the column names ``column_1_c1`` and ``column_1_c2``.

