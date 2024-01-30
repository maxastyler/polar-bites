from typing import Sequence, Union, Optional, Callable, Any

import numpy as np
import polars as pl
from attr import frozen, field


@frozen
class Column:
    """
    A class to define a column to be used in loading experiment data
    """

    names: Union[str, Sequence[str]] = field(
        converter=lambda x: [x] if isinstance(x, str) else x
    )
    """The names to load from the data
    """
    rename: Optional[str] = field(default=None, kw_only=True)
    """Rename the column names to the given name
    """
    as_type: Optional[type] = field(default=None, kw_only=True)
    """Cast the values of the column to the given type
    """
    is_array: bool = field(default=False, kw_only=True)
    """If true, transform the numpy array to a list of floats
    """
    pre_transform: Optional[Callable[[Any], Any]] = field(default=None, kw_only=True)
    """A function to apply to values before they are included in the dataframe
    """


def ensure_list_of_columns(columns: Optional[list[Union[str, Column]]]) -> list[Column]:
    """Create a list of columns from values which can be converted to columns"""
    return (
        []
        if columns is None
        else [
            column if isinstance(column, Column) else Column(column)
            for column in columns
        ]
    )


def polars_numerical_type_from_numpy_type(t: np.dtype) -> pl.PolarsDataType:
    if t.type is np.int32:
        return pl.Int32
    elif t.type is np.int64:
        return pl.Int64
    elif t.type is np.uint32:
        return pl.UInt32
    elif t.type is np.uint64:
        return pl.UInt64
    elif t.type is np.float32:
        return pl.Float32
    elif t.type is np.float64:
        return pl.Float64
    else:
        raise ValueError(f"Unsupported data type {t}")


def polars_array_type_from_numpy_array(array: np.ndarray) -> pl.PolarsDataType:
    """Take a numpy array and convert it to the equivalent polars array type"""

    dims = list(reversed(array.shape))

    t = pl.Array(polars_numerical_type_from_numpy_type(array.dtype), dims[0])

    for size in dims[1:]:
        t = pl.Array(t, size)

    return t
