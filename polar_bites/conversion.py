from typing import TypeVar, Any, Sequence

import numpy as np

T = TypeVar("T")


def numpy_arrays_to_lists(
    dictionary: dict[T, Any], array_keys: Sequence[T]
) -> dict[T, Any]:
    """Flatten and convert to float all of the keys inside dictionary which are in `array_keys`"""
    return {
        k: [float(x) for x in np.array(v).flatten()] if k in array_keys else v
        for k, v in dictionary.items()
    }


def flatten_dict(
    dictionary: dict[str, Any], key_separator: str = "_", recursive: bool = False
) -> dict[str, Any]:
    """Flatten the dictionaries inside the given dictionary, joining the keys by the given key_separator.
    If recursive, then perform the flattening recursively
    """
    new_dict = {}
    for k, v in dictionary.items():
        if isinstance(v, dict):
            new_dict |= {
                f"{k}{key_separator}{kk}": vv
                for kk, vv in (
                    flatten_dict(v, key_separator, recursive) if recursive else v
                ).items()
            }
        else:
            new_dict[k] = v
    return new_dict


def unflatten_dict(
    dictionary: dict[str, Any], key_separator: str = "_"
) -> dict[str, Any]:
    """Unflatten a flattened dict with keys separated by `key_separator`"""
    new_dict = {}
    for k, v in dictionary.items():
        dict_ref = new_dict
        [s, *rest] = k.split(key_separator)
        while len(rest) > 0:
            dict_ref = dict_ref.setdefault(s, {})
            s = rest.pop(0)
        dict_ref[s] = v
    return new_dict


def list_of_dicts_to_dict_of_lists(
    list_of_dicts: list[dict[str, T]]
) -> dict[str, list[T]]:
    """
    Transpose a list of dictionaries (rows of data) into a dictionary of lists (columns of data)
    """
    elements = {}
    for row in list_of_dicts:
        for k, v in row.items():
            elements.setdefault(k, []).append(v)
    return elements


def dict_of_lists_to_list_of_dicts(
    dict_of_lists: dict[str, list[T]]
) -> list[dict[str, T]]:
    """Transpose a dict of lists (columns of data) into a list of dictionaries (rows of data)"""
    assoc_lists = zip(*[[(k, v) for v in vs] for k, vs in dict_of_lists.items()])
    return [{a: b for (a, b) in assoc_list} for assoc_list in assoc_lists]
