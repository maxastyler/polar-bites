import numpy as np
import polars as pl

from polar_bites.manipulation import (
    iterate_over_variables,
    merge,
    partition,
    extract_tensor,
)


def test_iterate_over_variables():
    df = pl.DataFrame(
        {"v1": [0, 0, 1, 1, 2, 2], "v2": [2, 2, 2, 0, 1, 0], "v3": [0, 1, 2, 3, 4, 5]}
    )
    assert [
        (vars, row)
        for (vars, frame) in iterate_over_variables(df, ("v1", "v2"))
        for row in frame.rows()
    ] == [
        ((0, 2), (0, 2, 0)),
        ((0, 2), (0, 2, 1)),
        ((1, 0), (1, 0, 3)),
        ((1, 2), (1, 2, 2)),
        ((2, 0), (2, 0, 5)),
        ((2, 1), (2, 1, 4)),
    ]


def test_merge():
    frame_a = pl.DataFrame(
        {"a": [1, 2, 3], "b": [4, 5, 6], "c": [0, 0, 0], "d": [0, 0, 0]}
    )
    frame_b = pl.DataFrame(
        {"a": [1, 2, 4], "b": [4, 4, 6], "c": [1, 1, 1], "d": [1, 1, 1]}
    )
    result = pl.DataFrame(
        {
            "a": [1, 2, 2, 3, 4],
            "b": [4, 4, 5, 6, 6],
            "c": [1, 1, 0, 0, 1],
            "d": [1, 1, 0, 0, 1],
        }
    )
    assert (
        merge(frame_a, frame_b, ["a", "b"], ["c", "d"])
        .sort(["a", "b"])
        .equals(result.sort(["a", "b"]))
    )


def test_partition():
    df_1 = pl.DataFrame({"a": [1, 1], "b": [2, 3], "c": ["a", "b"]})
    df_2 = pl.DataFrame({"a": [2, 2], "b": [4, 5], "c": ["c", "d"]})
    original_dict = {(1,): df_1, (2,): df_2}
    df = pl.concat(original_dict.values())
    sdf = partition(df, ["a"])
    for k, v in original_dict.items():
        assert sdf[k].equals(v)


def test_extract_tensor():
    shape = (20, 30, 5, 10)

    g = np.random.randint(0, 10, shape)
    axes = [(f"ax_{i}", np.sort(np.random.rand(s))) for i, s in enumerate(shape)]
    df = pl.DataFrame(
        {
            a_name: grid.flatten()
            for ((a_name, _), grid) in zip(
                axes, np.meshgrid(*[cs for (_, cs) in axes], indexing="ij")
            )
        }
        | {"v": g.flatten()}
    )

    np.allclose(extract_tensor(df, [a for (a, _) in axes], "v", 0)[1], g)
