import io

import numpy as np
import polars as pl
from scipy.io import savemat

from polar_bites.column import Column
from polar_bites.conversion import dict_of_lists_to_list_of_dicts
from polar_bites.mat import (
    load_mat_to_dict,
    load_mat_to_dataframe,
    convert_dict_to_dataframe,
)


def test_loading_matlab_file_to_dict():
    test_data = [{"a": {"b": i, "c": i}, "d": np.array([i, i])} for i in range(100)]
    with io.BytesIO() as f:
        savemat(f, {"test_data": test_data})
        assert load_mat_to_dict(f, "test_data", ["d"]) == {
            n: [i for i in range(100)] for n in ["a_b", "a_c"]
        } | {"d": [[float(i), float(i)] for i in range(100)]}


def test_converting_dict_to_dataframe():
    a = [
        {
            n: [1, 2, 3],
            "other": [True, False, False],
            "unused_data": [0, 0, 0],
            "np_col": [np.random.rand(2, 2) for _ in range(3)],
        }
        for n in ["a", "b"]
    ]
    frames = [
        convert_dict_to_dataframe(
            i,
            columns=[
                Column(
                    ["a", "b"],
                    rename="renamed_column",
                    pre_transform=lambda x: x + 1,
                    as_type=pl.Int64,
                ),
                Column("other", as_type=pl.Int64),
                Column("np_col", is_array=True),
            ],
        )
        for i in a
    ]
    assert frames[0].columns == frames[1].columns
    assert frames[0].columns == ["renamed_column", "other"]
    assert frames[0]["other"].dtype == pl.Int64
    assert (frames[0]["renamed_column"] == [2, 3, 4]).all()


def test_load_mat_to_dict():
    with io.BytesIO() as inmemoryfile:
        mem_dict = {"a": {"a": {"c": [4]}, "b": [3]}}
        savemat(inmemoryfile, mem_dict)
        d = load_mat_to_dict(inmemoryfile)
        assert d == {"a_c": [4], "b": [3]}


def test_convert_dict_to_dataframe():
    original_df = pl.DataFrame({"a": [2, 3, 4], "b": [3, 4, 5], "c": ["1", "2", "3"]})
    original_df.to_dict(as_series=False)
    with io.BytesIO() as inmemoryfile:
        savemat(
            inmemoryfile,
            {
                "data": dict_of_lists_to_list_of_dicts(
                    original_df.to_dict(as_series=False)
                )
            },
        )
        d = load_mat_to_dataframe(
            inmemoryfile, columns=[Column("a"), Column("b"), Column("c")]
        )
        assert d.frame_equal(original_df)
