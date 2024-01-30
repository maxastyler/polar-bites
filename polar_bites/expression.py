import operator
from functools import reduce
from typing import Callable

import polars as pl


def filter_expression_generator(rf: Callable, *exps, **kexps) -> pl.Expr:
    """
    Generate an expression for use with polars' `filter` function.
    The function `rf` is used as a reducing function to combine the expressions together.
    :param rf: The reducing function (e.g. &, |) used to combine the expressions
    :param exp: An expression
    :param exps: Extra expressions
    :param kexps: keyword = value arguments which will be converted to pl.col(keyword) == value
    :return: The combined expression
    """
    total_exps = list(exps) + [pl.col(k) == v for k, v in kexps.items()]
    if len(total_exps) == 0:
        raise ValueError("Filter expression generator called without expressions")
    else:
        return reduce(rf, total_exps)


def afx(*exps, **kwargs) -> pl.Expr:
    """Combine the given expressions with the & operator"""
    return filter_expression_generator(operator.and_, *exps, **kwargs)


def ofx(*exps, **kwargs) -> pl.Expr:
    """Combine the given expressions with the | operator"""
    return filter_expression_generator(operator.or_, *exps, **kwargs)


__all__ = ["afx", "ofx"]
