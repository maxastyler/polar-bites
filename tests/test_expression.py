import polars as pl
from pytest import raises

import polar_bites as pb


def test_filter_expression_generation():
    e1 = pl.col("a") == 3
    e2 = pl.col("b") == 4
    e3 = pl.col("c") == 5
    full_expr = e1 & e2 & e3
    assert full_expr.meta == pb.expression.afx(e1, e2, c=5)
    assert full_expr.meta == pb.expression.afx(a=3, b=4, c=5)

    e1 = pl.col("a") == 3
    e2 = pl.col("b") == 4
    e3 = pl.col("c") == 5
    full_expr = e1 | e2 | e3
    assert full_expr.meta == pb.expression.ofx(e1, e2, c=5)
    with raises(ValueError):
        pb.expression.ofx()
