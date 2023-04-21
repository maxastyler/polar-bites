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
    """
    array_transform_keys = array_transform_keys or []
    loaded = loadmat(filename, simplify_cells=True)
    loaded = loaded[
        [k for k in loaded.keys() if not (k.startswith("__") and k.endswith("__"))][0]
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
    using the columns to perform various transformations on the data"""
    renames = {
        n: (c.rename if c.rename is not None else n) for c in columns for n in c.names
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
        [n for (n, t) in zip(new_frame.columns, new_frame.dtypes) if t == pl.Object]
    ).with_columns(types)


def load_mat_to_dataframe(
        filename: Union[Path, str],
        *,
        var_name: Optional[str] = None,
        columns: Optional[list[Union[str, Column]]] = None,
) -> pl.DataFrame:
    """
    Load the given mat file to a dataframe

    var_name is the variable name to extract from the file

    columns is a list of the columns to include in the dataframe, with optional types

    array_transform_keys flattens the given keys into lists

    `pre_transform` allows you to apply a function to the given column before conversion to dataframe

    `rename` is a dictionary of column renaming mappings
    """
    columns = ensure_list_of_columns(columns)
    array_transform_keys = [
        name for column in columns for name in column.names if column.is_array
    ]

    new_dict = load_mat_to_dict(filename, var_name, array_transform_keys)
    return convert_dict_to_dataframe(new_dict, columns)
