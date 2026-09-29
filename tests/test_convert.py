"""Tests for `camina.convert`."""

from __future__ import annotations

import collections
import dataclasses
import datetime
import pathlib

import pytest

import camina
from camina import convert


class TestDictify:
    def test_mutable_mapping_returned_as_is(self) -> None:
        item = {"a": 1}
        assert camina.dictify(item) is item

    def test_other_mappings(self) -> None:
        import types

        result = camina.dictify(types.MappingProxyType({"a": 1}))
        assert result == {"a": 1}
        assert isinstance(result, dict)

    def test_pairs(self) -> None:
        assert camina.dictify([("a", 1), ("b", 2)]) == {"a": 1, "b": 2}

    @pytest.mark.parametrize("item", [5, "ab", [1, 2], None])
    def test_unsupported(self, item: object) -> None:
        with pytest.raises(TypeError):
            camina.dictify(item)


class TestHashify:
    def test_hashable_returned_as_is(self) -> None:
        assert camina.hashify("a") == "a"
        assert camina.hashify(3) == 3
        assert camina.hashify((1, 2)) == (1, 2)

    def test_unhashable(self) -> None:
        assert camina.hashify([1, [2, 3]]) == (1, (2, 3))
        assert camina.hashify({"a": [1]}) == (("a", (1,)),)
        assert camina.hashify({1, 2}) == frozenset({1, 2})
        assert hash(camina.hashify([{"a": {1}}])) is not None

    def test_unhashable_object(self) -> None:
        @dataclasses.dataclass
        class Unhashable:
            value: int = 1

        result = camina.hashify(Unhashable())
        assert str(result).endswith("Unhashable(value=1)")

    def test_tuple_with_unhashable_content(self) -> None:
        assert camina.hashify(([1],)) == ((1,),)


class TestInstancify:
    def test_class(self) -> None:
        @dataclasses.dataclass
        class Thing:
            a: int = 0

        result = camina.instancify(Thing, a=5)
        assert isinstance(result, Thing)
        assert result.a == 5

    def test_instance(self) -> None:
        @dataclasses.dataclass
        class Thing:
            a: int = 0

        thing = Thing()
        result = camina.instancify(thing, a=2, b=3)
        assert result is thing
        assert thing.a == 2
        assert thing.b == 3  # type: ignore[attr-defined]


class TestIntegerify:
    def test_int(self) -> None:
        assert camina.integerify(4) == 4

    def test_float_and_str(self) -> None:
        assert camina.integerify(4.9) == 4
        assert camina.integerify("12") == 12
        assert convert.float_to_int(2.5) == 2
        assert convert.str_to_int("7") == 7

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError):
            camina.integerify([1])
        with pytest.raises(ValueError, match="invalid literal"):
            camina.integerify("x")


class TestIterify:
    def test_none(self) -> None:
        assert list(camina.iterify(None)) == []

    def test_str_and_bytes(self) -> None:
        assert list(camina.iterify("abc")) == ["abc"]
        assert list(camina.iterify(b"abc")) == [b"abc"]

    def test_iterable_is_returned_as_is(self) -> None:
        item = [1, 2]
        assert camina.iterify(item) is item
        assert list(camina.iterify({"a": 1})) == ["a"]
        assert list(camina.iterify(range(2))) == [0, 1]

    def test_non_iterable(self) -> None:
        assert list(camina.iterify(5)) == [5]


class TestKwargify:
    def test_dataclass(self) -> None:
        @dataclasses.dataclass
        class Thing:
            a: int
            b: str = "x"
            c: float = dataclasses.field(default=0.0, init=False)

        assert camina.kwargify(Thing, (1, "y")) == {"a": 1, "b": "y"}
        assert camina.kwargify(Thing, (1,)) == {"a": 1}

    def test_annotated_class_with_parent(self) -> None:
        class Parent:
            a: int

        class Child(Parent):
            b: int

        assert camina.kwargify(Child, (1, 2)) == {"a": 1, "b": 2}

    def test_too_many_args(self) -> None:
        @dataclasses.dataclass
        class Thing:
            a: int = 0

        with pytest.raises(ValueError, match="too many args"):
            camina.kwargify(Thing, (1, 2))


class TestListify:
    def test_none(self) -> None:
        assert camina.listify(None) == []
        assert camina.listify(None, default="x") == "x"
        assert camina.listify(None, default="None") is None
        assert camina.listify(None, default="none") is None

    def test_list_is_returned_as_is(self) -> None:
        item = [1, 2]
        assert camina.listify(item) is item

    def test_str_and_single_items(self) -> None:
        assert camina.listify("abc") == ["abc"]
        assert camina.listify(5) == [5]
        assert camina.listify({"a": 1}) == [{"a": 1}]

    def test_other_collections(self) -> None:
        assert camina.listify((1, 2)) == [1, 2]
        assert camina.listify({3}) == [3]
        assert camina.listify(x for x in range(2)) == [0, 1]


class TestNumify:
    @pytest.mark.parametrize(
        ("item", "expected"),
        [("3", 3), ("3.5", 3.5), (4, 4), (4.5, 4.5), (" 7 ", 7), ("-2", -2)],
    )
    def test_convertible(self, item: object, expected: float) -> None:
        result = camina.numify(item)
        assert result == expected
        assert type(result) is type(expected)

    @pytest.mark.parametrize("item", ["abc", None, [1]])
    def test_not_convertible(self, item: object) -> None:
        assert camina.numify(item) == item
        with pytest.raises(TypeError, match="not able to be converted"):
            camina.numify(item, raise_error=True)


class TestPathlibify:
    def test_str(self) -> None:
        assert camina.pathlibify("a/b") == pathlib.Path("a/b")

    def test_path(self) -> None:
        path = pathlib.Path("a")
        assert camina.pathlibify(path) is path

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError):
            camina.pathlibify(5)  # type: ignore[arg-type]


class TestStringify:
    def test_none(self) -> None:
        assert camina.stringify(None) == ""
        assert camina.stringify(None, default="x") == "x"
        assert camina.stringify(None, default="None") is None

    def test_str(self) -> None:
        assert camina.stringify("abc") == "abc"

    def test_sequence(self) -> None:
        assert camina.stringify(["a", "b"]) == "a, b"
        assert camina.stringify((1, 2)) == "1, 2"

    def test_unsupported(self) -> None:
        with pytest.raises(TypeError):
            camina.stringify(5)
        with pytest.raises(TypeError):
            camina.stringify(b"ab")


class TestTuplify:
    def test_none(self) -> None:
        assert camina.tuplify(None) == ()
        assert camina.tuplify(None, default="x") == "x"
        assert camina.tuplify(None, default="None") is None

    def test_tuple_is_returned_as_is(self) -> None:
        item = (1, 2)
        assert camina.tuplify(item) is item

    def test_str_is_not_iterated(self) -> None:
        assert camina.tuplify("abc") == ("abc",)

    def test_collections(self) -> None:
        assert camina.tuplify([1, 2]) == (1, 2)
        assert camina.tuplify({1}) == (1,)
        assert camina.tuplify(range(2)) == (0, 1)

    def test_single_items(self) -> None:
        assert camina.tuplify(5) == (5,)
        assert camina.tuplify({"a": 1}) == ({"a": 1},)


class TestTypify:
    @pytest.mark.parametrize(
        ("item", "expected"),
        [
            ("5", 5),
            ("5.5", 5.5),
            ("True", True),
            ("yes", True),
            ("false", False),
            ("No", False),
            ("a, 1, 2.5, true", ["a", 1, 2.5, True]),
            ("plain", "plain"),
        ],
    )
    def test_strings(self, item: str, expected: object) -> None:
        result = camina.typify(item)
        assert result == expected
        assert type(result) is type(expected)

    def test_non_str(self) -> None:
        assert camina.typify(5) == 5
        assert camina.typify(None) is None


class TestWindowify:
    def test_basic(self) -> None:
        assert list(camina.windowify([1, 2, 3, 4], 2)) == [
            (1, 2),
            (2, 3),
            (3, 4),
        ]

    def test_fill_value(self) -> None:
        assert list(camina.windowify([1, 2], 3, fill_value=0)) == [(1, 2, 0)]
        assert list(camina.windowify([], 2)) == [(None, None)]

    def test_step(self) -> None:
        assert list(camina.windowify([1, 2, 3, 4, 5], 2, step=2)) == [
            (1, 2),
            (3, 4),
            (5, None),
        ]
        assert list(camina.windowify([1, 2, 3, 4, 5, 6], 3, step=3)) == [
            (1, 2, 3),
            (4, 5, 6),
        ]

    def test_zero_length(self) -> None:
        assert list(camina.windowify([1, 2], 0)) == [()]

    def test_errors_are_raised_immediately(self) -> None:
        with pytest.raises(ValueError, match="length"):
            camina.windowify([1], -1)
        with pytest.raises(ValueError, match="step"):
            camina.windowify([1], 1, step=0)

    def test_generator_input(self) -> None:
        assert list(camina.windowify((i for i in range(3)), 2)) == [
            (0, 1),
            (1, 2),
        ]


class TestSpecificConverters:
    def test_to_int(self) -> None:
        assert convert.to_int(3) == 3
        assert convert.to_int(3.7) == 3
        assert convert.to_int("8") == 8
        with pytest.raises(TypeError):
            convert.to_int([1])

    def test_to_index(self) -> None:
        assert convert.to_index(3) == 3
        assert convert.to_index("4") == 4
        assert convert.to_index(5.0) == 5
        assert convert.str_to_index("6") == 6
        with pytest.raises(ValueError, match="whole number"):
            convert.to_index(5.5)
        with pytest.raises(TypeError):
            convert.to_index([1])

    def test_to_dict(self) -> None:
        assert convert.to_dict([("a", 1)]) == {"a": 1}
        assert convert.to_dict(collections.OrderedDict(a=1)) == {"a": 1}
        assert type(convert.to_dict(collections.OrderedDict(a=1))) is dict
        with pytest.raises(TypeError):
            convert.to_dict(5)

    def test_to_list(self) -> None:
        item = [1]
        assert convert.to_list(item) is item
        assert convert.to_list((1, 2)) == [1, 2]
        assert convert.to_list("[1, 'a']") == [1, "a"]
        assert convert.str_to_list("[3]") == [3]
        with pytest.raises(TypeError):
            convert.to_list(5)
        with pytest.raises(TypeError, match="not a list"):
            convert.to_list("5")
        with pytest.raises(ValueError, match="not a valid"):
            convert.to_list("[1,")

    def test_to_float(self) -> None:
        assert convert.to_float(1.5) == 1.5
        assert convert.to_float(2) == 2.0
        assert isinstance(convert.to_float(2), float)
        assert convert.to_float("3.5") == 3.5
        assert convert.int_to_float(4) == 4.0
        assert convert.str_to_float("0.25") == 0.25
        with pytest.raises(TypeError):
            convert.to_float([1])

    def test_to_path(self) -> None:
        assert convert.to_path("a") == pathlib.Path("a")
        assert convert.to_path(pathlib.Path("b")) == pathlib.Path("b")
        assert convert.str_to_path("c") == pathlib.Path("c")
        with pytest.raises(TypeError):
            convert.to_path(5)

    def test_to_str(self) -> None:
        assert convert.to_str("a") == "a"
        assert convert.to_str(5) == "5"
        assert convert.to_str(1.5) == "1.5"
        assert convert.to_str(["a", 1]) == "a, 1"
        assert convert.to_str(None) == "None"
        assert convert.to_str(pathlib.PurePosixPath("a/b")) == "a/b"
        assert convert.int_to_str(2) == "2"
        assert convert.float_to_str(2.5) == "2.5"
        assert convert.list_to_str(["x", "y"]) == "x, y"
        assert convert.none_to_str(None) == "None"
        assert convert.path_to_str(pathlib.PurePosixPath("z")) == "z"
        with pytest.raises(TypeError):
            convert.to_str({1})

    def test_datetime_to_str(self) -> None:
        moment = datetime.datetime(2024, 1, 2, 3, 4)  # noqa: DTZ001
        assert convert.to_str(moment) == "2024-01-02_03-04"
        assert convert.datetime_to_str(moment, "%Y") == "2024"
        assert convert.datetime_to_str(moment, None) == "2024-01-02_03-04"
        assert convert.datetime_to_string is convert.datetime_to_str
