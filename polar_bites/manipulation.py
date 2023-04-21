from typing import Sequence, Iterator, Union

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
        old.join(new, on=on, how="outer")
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
