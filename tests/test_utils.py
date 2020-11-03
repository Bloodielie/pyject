from typing import Union, List, Iterator, Optional

from pyject.utils import check_generic_typing, check_union_typing
from pytest import fixture


@fixture()
def collection_type_names():
    return {"Any", "Set", "List", "Tuple", "FrozenSet", "Sequence", "Iterator"}


def test_check_generic_typing(collection_type_names):
    assert check_generic_typing(List[str], collection_type_names) is True
    assert check_generic_typing(Iterator[str], collection_type_names) is True
    assert check_generic_typing(Union[str, int], collection_type_names) is False
    assert check_generic_typing(Optional[str], collection_type_names) is False


def test_check_union_typing():
    assert check_union_typing(List[str]) is False
    assert check_union_typing(Iterator[str]) is False
    assert check_union_typing(Union[str, int]) is True
    assert check_union_typing(Optional[str]) is True

