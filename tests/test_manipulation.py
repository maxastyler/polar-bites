import polars as pl

from polar_bites.manipulation import iterate_over_variables, merge


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
        .frame_equal(result.sort(["a", "b"]))
    )
