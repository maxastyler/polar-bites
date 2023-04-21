import io

import polars as pl
from scipy.io import savemat

from polar_bites.column import Column
from polar_bites.conversion import dict_of_lists_to_list_of_dicts
from polar_bites.mat import load_mat_to_dict, load_mat_to_dataframe


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
        savemat(inmemoryfile, {"data": dict_of_lists_to_list_of_dicts(original_df.to_dict(as_series=False))})
        d = load_mat_to_dataframe(inmemoryfile, columns=[Column("a"), Column("b"), Column("c")])
        assert d.frame_equal(original_df)
