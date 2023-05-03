import operator
from typing import Callable

import polars as pl


def filter_expression_generator(rf: Callable, exp, *exps, **kexps) -> pl.Expr:
    """
    Generate an expression for use with polars' `filter` function.
    The function `rf` is used as a reducing function to combine the expressions together.
    :param rf: The reducing function (e.g. &, |) used to combine the expressions
    :param exp: An expression
    :param exps: Extra expressions
    :param kexps: keyword = value arguments which will be converted to pl.col(keyword) == value
    :return: The combined expression
    """
    for e in exps:
        exp = rf(exp, e)
    for k, v in kexps.items():
        exp = rf(exp, pl.col(k) == v)
    return exp


def afx(exp, *exps, **kwargs) -> pl.Expr:
    return filter_expression_generator(operator.and_, exp, *exps, **kwargs)


def ofx(exp, *exps, **kwargs) -> pl.Expr:
    return filter_expression_generator(operator.or_, exp, *exps, **kwargs)
