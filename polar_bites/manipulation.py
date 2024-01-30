from typing import Sequence, Iterator, Union, Any

import numpy as np
import polars as pl


def iterate_over_variables(
    dataframe: pl.DataFrame,
    variables: Sequence[str],
    sort: bool = True,
    output_as_dict: bool = False,
) -> Iterator[tuple[Union[tuple, dict[str, object]], pl.DataFrame]]:
    """Create an iterator over the unique values of the given variables,
    sorting in the order they come in

    If output_as_dict is False, the first element of the output tuple is a tuple of the variables iterated over
    If output_as_dict is True, the first element of the output tuple is a dict of the variables iterated over

    :returns: An iterator over the different unique combinations of column values, and the corresponding dataframe.
    """
    [current_var, *rest] = variables
    values = dataframe[current_var].unique()
    if sort:
        values = values.sort()
    for value in values:
        filtered_frame = dataframe.filter(pl.col(current_var) == value)
        if len(rest) > 0:
            for vars, loop_df in iterate_over_variables(
                filtered_frame, rest, sort, output_as_dict=output_as_dict
            ):
                if output_as_dict:
                    yield {current_var: value} | vars, loop_df
                else:
                    yield (value, *vars), loop_df
        else:
            if output_as_dict:
                yield {current_var: value}, filtered_frame
            else:
                yield (value,), filtered_frame


def merge(
    old: pl.DataFrame,
    new: pl.DataFrame,
    on: Union[str, pl.Expr, Sequence[Union[str, pl.Expr]]],
    to_merge: Union[str, Sequence[str]],
) -> pl.DataFrame:
    """Given two dataframes, merge the values from the new one into the old one, replacing any
    :param old: The old data
    :param new: The new data
    :param on: The columns to join on
    :param to_merge: The columns with new data to overwrite with
    :returns: The merged dataframe
    """
    if isinstance(to_merge, str):
        to_merge = [to_merge]
    merge_expressions = [
        pl.when(pl.col(f"{column}_right").is_not_null())
        .then(pl.col(f"{column}_right"))
        .otherwise(pl.col(column))
        .alias(column)
        for column in to_merge
    ]
    return (
        old.join(new, on=on, how="outer_coalesce")
        .with_columns(merge_expressions)
        .drop([f"{column}_right" for column in to_merge])
    )


def partition(
    dataframe: pl.DataFrame, variables: Sequence[str]
) -> dict[tuple, pl.DataFrame]:
    """Partition a dataframe based on the given variables.
    Returns a dictionary which is indexed by the tuple of the variables, each value being all the values
    in the original dataframe with those tuple variables"""
    return {
        vars: df
        for vars, df in iterate_over_variables(
            dataframe, variables=variables, output_as_dict=False
        )
    }


def extract_tensor(
    dataframe: pl.DataFrame,
    coordinate_columns: Sequence[str],
    value_column: str,
    fill: Any,
) -> tuple[list[np.ndarray], np.ndarray]:
    """Given the sequence of coordinate columns, create a sparse (probably irregularly spaced) tensor,
    with any empty spaces filled with the fill value and return ([list of coordinates], tensor)
    """

    shape = []
    coordinates_list = []
    for c in coordinate_columns:
        coordinates = dataframe.select(pl.col(c).unique().sort())
        coordinates_list.append(coordinates.to_numpy())
        index_frame = coordinates.with_columns(
            pl.col(c).cumcount().alias(f"{c}_index") - 1
        )
        shape.append(len(index_frame))
        dataframe = dataframe.join(index_frame, on=c)

    tensor = np.full(shape, fill)
    for [v, *indices] in dataframe.select(
        [value_column, *[f"{c}_index" for c in coordinate_columns]]
    ).rows():
        tensor[tuple(indices)] = v

    return coordinates_list, tensor
