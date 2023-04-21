from typing import Any

from hypothesis import strategies as st, given

from polar_bites.conversion import (
    dict_of_lists_to_list_of_dicts,
    list_of_dicts_to_dict_of_lists,
)


def dict_strat(value_strat):
    return st.dictionaries(keys=st.text(), values=value_strat)


def dict_of_lists_strategy(n: int) -> st.SearchStrategy[dict[str, list[int]]]:
    return st.dictionaries(
        keys=st.text(),
        values=st.lists(st.integers(), min_size=n, max_size=n),
        min_size=1,
    )


@given(input=st.integers(min_value=1, max_value=100).flatmap(dict_of_lists_strategy))
def test_list_of_dicts_to_dict_of_lists_isomorphism(input):
    assert (
        list_of_dicts_to_dict_of_lists(dict_of_lists_to_list_of_dicts(input)) == input
    )


separator = st.text(min_size=1)


def recursive_dict_strategy(blacklist_chars: str) -> st.SearchStrategy[dict[str, Any]]:
    name_strings = st.text(alphabet=st.characters(blacklist_characters=blacklist_chars))

    return st.recursive(
        st.dictionaries(keys=name_strings, values=st.integers(), min_size=1),
        lambda x: st.dictionaries(keys=name_strings, values=x, min_size=1),
    )


#
# @given(
#     input=separator.flatmap(lambda s: st.tuples(st.just(s), recursive_dict_strategy(s)))
# )
# def test_dict_flattening_strategy(input: tuple[str, dict]):
#     separator, dictionary = input
#     assert unflatten_dict(flatten_dict(dictionary, separator), separator) == dictionary
