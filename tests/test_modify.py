"""Tests for `camina.modify`."""

from __future__ import annotations

import collections
import dataclasses
import types
from typing import Any

import pytest

import camina
from camina import modify


@dataclasses.dataclass
class Named:
    name: str = "thing"


class Item:
    def __init__(self, name: str) -> None:
        self.name = name


def _function_named(name: str) -> Any:
    def function() -> None:
        pass

    function.__name__ = name
    return function


class TestAddPrefix:
    def test_str(self) -> None:
        assert camina.add_prefix("a", "pre") == "prea"
        assert camina.add_prefix("a", "pre", "_") == "pre_a"
        assert camina.add_prefix("a", "pre", None) == "prea"
        assert modify.add_prefix_to_str("a", prefix="x", divider="-") == "x-a"

    def test_dict(self) -> None:
        result = camina.add_prefix({"a": 1, "b": 2}, "p", "_")
        assert result == {"p_a": 1, "p_b": 2}
        assert modify.add_prefix_to_dict({"a": 1}, "p") == {"pa": 1}

    def test_list(self) -> None:
        assert camina.add_prefix(["a", "b"], "p", "_") == ["p_a", "p_b"]
        assert modify.add_prefix_to_list(["a"], "p") == ["pa"]

    def test_set(self) -> None:
        assert camina.add_prefix({"a", "b"}, "p") == {"pa", "pb"}
        assert modify.add_prefix_to_set({"a"}, "p") == {"pa"}
        assert camina.add_prefix(frozenset({"a"}), "p") == frozenset({"pa"})

    def test_tuple(self) -> None:
        assert camina.add_prefix(("a", "b"), "p", "_") == ("p_a", "p_b")
        assert modify.add_prefix_to_tuple(("a",), "p") == ("pa",)

    def test_recursive(self) -> None:
        item = {"a": {"b": 1}, "c": ["d", ("e",)], "f": 5}
        result = camina.add_prefix(item, "p", recursive=True)
        assert result == {"pa": {"pb": 1}, "pc": ["pd", ("pe",)], "pf": 5}

    def test_not_recursive_leaves_nested_items(self) -> None:
        assert camina.add_prefix({"a": {"b": 1}}, "p") == {"pa": {"b": 1}}
        with pytest.raises(TypeError):
            camina.add_prefix(["a", ["b"]], "p")

    def test_original_is_unchanged_and_type_kept(self) -> None:
        original = collections.OrderedDict(a=1)
        result = camina.add_prefix(original, "p")
        assert original == {"a": 1}
        assert isinstance(result, collections.OrderedDict)
        default = collections.defaultdict(list, {"a": 1})
        result = camina.add_prefix(default, "p")
        assert isinstance(result, collections.defaultdict)
        assert result.default_factory is list

    def test_recursive_with_unsupported_nested_item(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.add_prefix(["a", 5], "p", recursive=True)

    def test_container_that_cannot_be_rebuilt(self) -> None:
        class Fixed(dict):
            def __init__(self) -> None:
                super().__init__(a=1)

        result = camina.add_prefix(Fixed(), "p")
        assert result == {"pa": 1}
        assert type(result) is dict

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.add_prefix(5, "p")


class TestAddSuffix:
    def test_str(self) -> None:
        assert camina.add_suffix("a", "suf") == "asuf"
        assert camina.add_suffix("a", "suf", "_") == "a_suf"
        assert modify.add_suffix_to_str("a", suffix="x", divider="-") == "a-x"

    def test_dict(self) -> None:
        assert camina.add_suffix({"a": 1}, "s", "_") == {"a_s": 1}
        assert modify.add_suffix_to_dict({"a": 1}, "s") == {"as": 1}

    def test_list(self) -> None:
        assert camina.add_suffix(["a", "b"], "s", "_") == ["a_s", "b_s"]
        assert modify.add_suffix_to_list(["a"], "s") == ["as"]

    def test_set(self) -> None:
        assert camina.add_suffix({"a"}, "s") == {"as"}
        assert modify.add_suffix_to_set({"a"}, "s") == {"as"}

    def test_tuple(self) -> None:
        assert camina.add_suffix(("a",), "s", "_") == ("a_s",)
        assert modify.add_suffix_to_tuple(("a",), "s") == ("as",)

    def test_recursive(self) -> None:
        result = camina.add_suffix({"a": ["b", {"c": 1}]}, "s", recursive=True)
        assert result == {"as": ["bs", {"cs": 1}]}

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.add_suffix(5, "s")

    def test_round_trip_with_drop_suffix(self) -> None:
        added = camina.add_suffix(["a", "b"], "x", "_")
        assert camina.drop_suffix(added, "x", "_") == ["a", "b"]


class TestAddSlots:
    def test_adds_slots(self) -> None:
        @dataclasses.dataclass
        class Plain:
            a: int = 1
            b: str = "x"

        slotted = camina.add_slots(Plain)
        assert slotted.__slots__ == ("a", "b")
        assert slotted.__name__ == "Plain"
        instance = slotted(a=2)
        assert instance.a == 2
        assert instance.b == "x"
        assert not hasattr(instance, "__dict__")
        with pytest.raises(AttributeError):
            instance.c = 3

    def test_already_slotted(self) -> None:
        @dataclasses.dataclass
        class Slotted:
            __slots__ = ("a",)
            a: int

        with pytest.raises(TypeError, match="already contains __slots__"):
            camina.add_slots(Slotted)

    def test_not_a_dataclass(self) -> None:
        class Plain:
            pass

        with pytest.raises(TypeError):
            camina.add_slots(Plain)


class TestCleave:
    def test_last_divider(self) -> None:
        assert camina.cleave("a_b_c") == ("a_b", "c")
        assert camina.cleave_str("a_b_c", "_", True) == ("a_b", "c")

    def test_first_divider(self) -> None:
        assert camina.cleave("a_b_c", return_last=False) == ("a", "b_c")

    def test_multi_character_divider(self) -> None:
        assert camina.cleave("a--b--c", "--") == ("a--b", "c")
        assert camina.cleave("a--b--c", "--", return_last=False) == (
            "a",
            "b--c",
        )

    def test_missing_divider(self) -> None:
        assert camina.cleave("abc") == ("abc", "abc")
        with pytest.raises(ValueError, match="is not in"):
            camina.cleave("abc", raise_error=True)

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.cleave(5, "_")


class TestSeparate:
    def test_separate(self) -> None:
        assert camina.separate("a_b_c") == ["a", "b", "c"]
        assert camina.separate("a, b", ", ") == ["a", "b"]
        assert modify.separate_str("a_b") == ["a", "b"]

    def test_missing_divider(self) -> None:
        assert camina.separate("abc") == ["abc"]
        with pytest.raises(ValueError, match="is not in"):
            camina.separate("abc", raise_error=True)

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.separate(5, "_")


class TestDeduplicate:
    def test_list(self) -> None:
        assert camina.deduplicate([1, 2, 1, 3, 2]) == [1, 2, 3]
        assert modify.deduplicate_list(["a", "a"]) == ["a"]

    def test_tuple(self) -> None:
        assert camina.deduplicate((1, 2, 1)) == (1, 2)
        assert modify.deduplicate_tuple((1, 1)) == (1,)

    def test_unhashable_items(self) -> None:
        assert camina.deduplicate([[1], [1], [2], {"a": 1}, {"a": 1}]) == [
            [1],
            [2],
            {"a": 1},
        ]

    def test_list_subclass(self) -> None:
        class MyList(list):
            pass

        result = camina.deduplicate(MyList([1, 1]))
        assert isinstance(result, MyList)
        assert result == [1]

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.deduplicate("aab")


class TestDropDunders:
    def test_dict(self) -> None:
        item = {"__a__": 1, "b": 2, "__c": 3, "_d": 4, 5: 5}
        result = camina.drop_dunders(item)
        assert result == {"b": 2, "__c": 3, "_d": 4, 5: 5}
        assert modify.drop_dunders_dict({"__x__": 1}) == {}

    def test_list(self) -> None:
        assert camina.drop_dunders(["__a__", "b", "__c", "_d"]) == [
            "b",
            "__c",
            "_d",
        ]
        assert modify.drop_dunders_list([]) == []

    def test_list_of_objects(self) -> None:
        items = [Item("__init__"), Item("keep")]
        assert [i.name for i in camina.drop_dunders(items)] == ["keep"]
        functions = [_function_named("__call__"), _function_named("keep")]
        assert [f.__name__ for f in camina.drop_dunders(functions)] == ["keep"]

    def test_set_and_tuple(self) -> None:
        assert camina.drop_dunders({"__a__", "b"}) == {"b"}
        assert camina.drop_dunders(("__a__", "b")) == ("b",)
        assert modify.drop_dunders_set({"__a__"}) == set()
        assert modify.drop_dunders_tuple(("__a__",)) == ()

    def test_unnamed_items(self) -> None:
        with pytest.raises(TypeError, match="name or __name__"):
            camina.drop_dunders([1, 2])

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.drop_dunders(5)


class TestDropPrefix:
    def test_str(self) -> None:
        assert camina.drop_prefix("pre_a", "pre") == "_a"
        assert camina.drop_prefix("pre_a", "pre", "_") == "a"
        assert camina.drop_prefix("a", "pre") == "a"
        assert modify.drop_prefix_from_str("xa", "x") == "a"

    def test_dict(self) -> None:
        assert camina.drop_prefix({"p_a": 1, "b": 2}, "p", "_") == {
            "a": 1,
            "b": 2,
        }
        assert modify.drop_prefix_from_dict({"pa": 1}, "p") == {"a": 1}

    def test_list(self) -> None:
        assert camina.drop_prefix(["p_a", "p_b"], "p", "_") == ["a", "b"]
        assert modify.drop_prefix_from_list(["pa"], "p") == ["a"]

    def test_set(self) -> None:
        assert camina.drop_prefix({"pa", "pb"}, "p") == {"a", "b"}
        assert modify.drop_prefix_from_set({"pa"}, "p") == {"a"}

    def test_tuple(self) -> None:
        assert camina.drop_prefix(("pa", "b"), "p") == ("a", "b")
        assert modify.drop_prefix_from_tuple(("pa",), "p") == ("a",)

    def test_round_trip_with_add_prefix(self) -> None:
        added = camina.add_prefix(["a", "b"], "x", "_")
        assert camina.drop_prefix(added, "x", "_") == ["a", "b"]

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.drop_prefix(5, "p")


class TestDropPrivates:
    def test_dict(self) -> None:
        item = {"_a": 1, "b": 2, "__c__": 3, 5: 5}
        assert camina.drop_privates(item) == {"b": 2, 5: 5}
        assert modify.drop_privates_dict({"_x": 1}) == {}

    def test_list(self) -> None:
        assert camina.drop_privates(["_a", "b", "__c__"]) == ["b"]
        assert modify.drop_privates_list([]) == []

    def test_list_of_objects(self) -> None:
        items = [Item("_hidden"), Item("shown"), Named()]
        result = camina.drop_privates(items)
        assert [i.name for i in result] == ["shown", "thing"]

    def test_set_and_tuple(self) -> None:
        assert camina.drop_privates({"_a", "b"}) == {"b"}
        assert camina.drop_privates(("_a", "b")) == ("b",)
        assert modify.drop_privates_set({"_a"}) == set()
        assert modify.drop_privates_tuple(("_a",)) == ()

    def test_mapping_type_is_kept(self) -> None:
        item = types.MappingProxyType({"_a": 1, "b": 2})
        result = camina.drop_privates(item)
        assert isinstance(result, types.MappingProxyType)
        assert dict(result) == {"b": 2}

    def test_unnamed_items(self) -> None:
        with pytest.raises(TypeError, match="name or __name__"):
            camina.drop_privates([1])

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.drop_privates(5)


class TestDropSubstring:
    def test_str(self) -> None:
        assert camina.drop_substring("abcabc", "b") == "acac"
        assert camina.drop_substring("abc", "z") == "abc"
        assert modify.drop_substring_from_str("abc", "c") == "ab"

    def test_dict(self) -> None:
        assert camina.drop_substring({"abc": 1}, "b") == {"ac": 1}
        assert modify.drop_substring_from_dict({"abc": 1}, "a") == {"bc": 1}

    def test_list(self) -> None:
        assert camina.drop_substring(["abc", "b"], "b") == ["ac", ""]
        assert modify.drop_substring_from_list(["abc"], "a") == ["bc"]

    def test_set(self) -> None:
        assert camina.drop_substring({"abc"}, "b") == {"ac"}
        assert modify.drop_substring_from_set({"abc"}, "a") == {"bc"}

    def test_tuple(self) -> None:
        assert camina.drop_substring(("abc",), "b") == ("ac",)
        assert modify.drop_substring_from_tuple(("abc",), "a") == ("bc",)

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.drop_substring(5, "p")


class TestDropSuffix:
    def test_str(self) -> None:
        assert camina.drop_suffix("a_suf", "suf") == "a_"
        assert camina.drop_suffix("a_suf", "suf", "_") == "a"
        assert camina.drop_suffix("a", "suf") == "a"
        assert modify.drop_suffix_from_str("ax", "x") == "a"

    def test_dict(self) -> None:
        assert camina.drop_suffix({"a_s": 1, "b": 2}, "s", "_") == {
            "a": 1,
            "b": 2,
        }
        assert modify.drop_suffix_from_dict({"as": 1}, "s") == {"a": 1}

    def test_list(self) -> None:
        assert camina.drop_suffix(["a_s", "b_s"], "s", "_") == ["a", "b"]
        assert modify.drop_suffix_from_list(["as"], "s") == ["a"]

    def test_set(self) -> None:
        assert camina.drop_suffix({"as", "bs"}, "s") == {"a", "b"}
        assert modify.drop_suffix_from_set({"as"}, "s") == {"a"}

    def test_tuple(self) -> None:
        assert camina.drop_suffix(("as", "b"), "s") == ("a", "b")
        assert modify.drop_suffix_from_tuple(("as",), "s") == ("a",)

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError, match="not a supported type"):
            camina.drop_suffix(5, "s")


class TestCaseConversion:
    @pytest.mark.parametrize(
        ("snake", "capital"),
        [
            ("snake_case", "SnakeCase"),
            ("word", "Word"),
            ("a_b_c", "ABC"),
            ("with_number_2", "WithNumber2"),
        ],
    )
    def test_capitalify(self, snake: str, capital: str) -> None:
        assert camina.capitalify(snake) == capital

    @pytest.mark.parametrize(
        ("capital", "snake"),
        [
            ("SnakeCase", "snake_case"),
            ("Word", "word"),
            ("HTTPServer", "http_server"),
            ("getHTTPResponseCode", "get_http_response_code"),
            ("already_snake", "already_snake"),
            ("Version2Update", "version2_update"),
        ],
    )
    def test_snakify(self, capital: str, snake: str) -> None:
        assert camina.snakify(capital) == snake

    def test_round_trip(self) -> None:
        assert (
            camina.snakify(camina.capitalify("some_long_name"))
            == "some_long_name"
        )


class TestUniquify:
    def test_unused_key(self) -> None:
        assert camina.uniquify("a", {"b": 1}) == "a"

    def test_used_key(self) -> None:
        assert camina.uniquify("a", {"a": 1}) == "a2"

    def test_repeated_use(self) -> None:
        dictionary = {"a": 1, "a2": 2, "a3": 3}
        assert camina.uniquify("a", dictionary) == "a4"

    def test_gap_is_not_filled_out_of_order(self) -> None:
        assert camina.uniquify("a", {"a": 1, "a3": 3}) == "a2"

    def test_index(self) -> None:
        assert camina.uniquify("a", {"a": 1}, index=4) == "a5"
        assert camina.uniquify("a", {"a": 1}, index=None) == "a2"
