from pathlib import Path
from typing import Union, Optional, Sequence, Any

import polars as pl
from scipy.io import loadmat

from .column import Column, ensure_list_of_columns
from .conversion import (
    list_of_dicts_to_dict_of_lists,
    numpy_arrays_to_lists,
    flatten_dict,
)

__all__ = [
    "load_mat_to_dict",
    "convert_dict_to_dataframe",
    "load_mat_to_dataframe",
]


def load_mat_to_dict(
    filename: Union[Path, str],
    var_name: Optional[str] = None,
    array_transform_keys: Optional[Sequence[str]] = None,
) -> dict[str, Any]:
    """Load a .mat file to a dictionary.
    var_name should be the variable that the data is stored under in the mat file.
    If this isn't given, then the first variable is loaded.
    Nested cells are flattening by joining their names with underscores
    The keys in array_transform_keys are converted from numpy arrays to lists of floats

    :param filename: the ``.mat``'s filename
    :param var_name: the variable to extract from the mat file
    :param array_transform_keys: the list of keys in the structure which should be converted from numpy arrays to lists of float
    """
    array_transform_keys = array_transform_keys or []
    loaded = loadmat(filename, simplify_cells=True)
    loaded = loaded[
        [
            k
            for k in loaded.keys()
            if not (k.startswith("__") and k.endswith("__"))
        ][0]
        if var_name is None
        else var_name
    ]
    if isinstance(loaded, dict):
        loaded = [loaded]
    data = list_of_dicts_to_dict_of_lists(
        [
            numpy_arrays_to_lists(
                flatten_dict(row, recursive=True), array_transform_keys
            )
            for row in loaded
        ]
    )
    return data


def convert_dict_to_dataframe(
    data_dict: dict[str, Any], columns: Sequence[Column]
) -> pl.DataFrame:
    """Convert a dictionary to a dataframe,
    using the columns to perform various transformations on the data

    :param data_dict: the dictionary containing the data to convert
    :param columns: the set of Columns describing the column transformations that should happen to this dictionary
    """
    renames = {
        n: (c.rename if c.rename is not None else n)
        for c in columns
        for n in c.names
    }
    transforms = {
        n: c.pre_transform
        for c in columns
        for n in c.names
        if c.pre_transform is not None
    }
    types = [
        pl.col(n).cast(c.as_type)
        for c in columns
        if c.as_type is not None
        for n in (c.names if c.rename is None else [c.rename])
    ]
    new_frame = pl.DataFrame(
        {
            renames[k]: [transforms[k](i) for i in v]
            if transforms.get(k) is not None
            else v
            for k, v in data_dict.items()
            if k in renames
        }
    )
    return new_frame.drop(
        [
            n
            for (n, t) in zip(new_frame.columns, new_frame.dtypes)
            if t == pl.Object
        ]
    ).with_columns(types)


def load_mat_to_dataframe(
    filename: Union[Path, str],
    *,
    var_name: Optional[str] = None,
    columns: Optional[list[Union[str, Column]]] = None,
) -> pl.DataFrame:
    """
    Load the given mat file to a dataframe

    :param filename: the filename to load the data from
    :param var_name: the variable name to extract from the file. If not given, then this function extracts the first variable from the `.mat` file
    :param columns: a list of the columns to include in the dataframe
    """
    columns = ensure_list_of_columns(columns)
    array_transform_keys = [
        name for column in columns for name in column.names if column.is_array
    ]

    new_dict = load_mat_to_dict(filename, var_name, array_transform_keys)
    return convert_dict_to_dataframe(new_dict, columns)
