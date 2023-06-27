Examples
========

A list of things you might want to do with :doc:`polar-bites <index>`.

Iterating over variables
------------------------

You can use the :func:`polar_bites.manipulation.iterate_over_variables` function to iterate over sub dataframes, grouped by the unique values of the variables. So, if you have a dataframe ``df`` with columns ``[col_1, col_2, col_3]``, then the function:

.. code-block:: python

   polar_bites.manipulation.iterate_over_variables(df, ["col_1", "col_2"]).keys()

Will return an iterator, which returns a tuple ``((col_1_value, col_2_value), filtered_datafrae)`` where the first element of the tuple contains a tuple which is the unique combination of values from the columns that you filtered on, and the second element of the tuple is the dataframe filtered by these unique values.

If the argument ``output_as_dict`` is ``True``, then the first element of the iterators tuples will be a dictionary mapping column name to unique value for each combination of unique values.

This is a nice function to use in a for loop:

.. code-block:: python

   for ((col_1, col_2), df) in polar_bites.manipulation.iterate_over_variables(df, ["col_1", "col_2"]).keys():
       print(col_1, col_2, df)


Extracting a tensor of values
-----------------------------

The :func:`polar_bites.manipulation.extract_tensor` allows you to extract a (possibly irregular) grid of values from the dataframe. This could be useful, for example, if you had data stored in a dataframe ``df`` with columns ``[x, y, z, value]`` where ``x,y,z`` are the coordinates and ``value`` is the value at those coords. You could extract a 3D numpy array with these values like so:

.. code-block:: python

   ([xs, ys, zs], value_cube) = extract_tensor(df, ["x", "y", "z"], "value", 0)

Where the points with missing value get filled with 0.

This returns 3 1D arrays in a list, which we have assigned to ``[xs, ys, zs]`` and are the coordinates along each axis, and also the cube of values.

Loading MATLAB files
--------------------

The function :func:`polar_bites.mat.load_mat_to_dataframe` is used to extract a structure array from a given ``.mat`` file.
It takes the filename of the ``.mat`` file, and optionally the name of the variable to extract, and the list of columns to extract. If not given a name, it will extract the first variable from the file. The list of columns allows for selection/transformation of the data before it is loaded into a dataframe.

Finding Keys
````````````
If you just want to find what keys are in a ``.mat`` file, you can use :func:`polar_bites.mat.load_mat_to_dict`:

.. code-block:: python

   polar_bites.mat.load_mat_to_dict("mat_file.mat").keys()

printing these ``keys()`` is what you need.

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


Filtering data
--------------
Filtering data in polars is a little unweildy, so I've written two helper functions: :func:`polar_bites.expression.afx` and :func:`polar_bites.expression.ofx` to ease this. These functions take in a variable amount of individual expressions, and ``&`` / ``|`` them together, respectively. They also take in keyword arguments to remove the need to write ``polars.col`` most of the time.
They can be used to shorten:

.. code-block:: python

   my_dataframe.filter(((pl.col("spacey column name") == 3) &
		        (pl.col("column_1") == True) & 
			(pl.col("column_2") == False)))
   
To something like:

.. code-block:: python

   my_dataframe.filter(pb.afx(pl.col("spacey column name") == 3,
		              column_1 = True,
			      column_2 = True))
and likewise for :func:`ofx<polar_bites.expression.ofx>`. This makes adding new clauses into the filter expression much nicer than directly inside the ``filter`` expression.
