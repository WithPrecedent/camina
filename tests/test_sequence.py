"""Tests for `camina.sequence`."""

from __future__ import annotations

import dataclasses

import pytest

import camina


@dataclasses.dataclass
class Sample:
    name: str = "something"


class TestListing:
    def test_basic_operations(self) -> None:
        listing = camina.Listing(contents=["a", "b", "c"])
        assert listing[1] == "b"
        listing.add(item="d")
        assert listing[3] == "d"
        listing.insert(2, "zebra")
        assert listing[2] == "zebra"
        listing.append("e")
        assert listing[5] == "e"
        listing.extend(["f", "g"])
        assert listing[7] == "g"
        sub_listing = listing.subset(
            include=["a", "b", "c", "d", "zebra"], exclude="d"
        )
        assert sub_listing.contents == ["a", "b", "zebra", "c"]
        sub_listing.remove("c")
        assert sub_listing.contents == ["a", "b", "zebra"]
        listing.clear()
        assert len(listing) == 0

    def test_add_extends_sequences_but_not_strings(self) -> None:
        listing = camina.Listing()
        listing.add("abc")
        listing.add(["d", "e"])
        listing.add(("f",))
        listing.add(5)
        listing.add(b"bytes")
        assert listing.contents == ["abc", "d", "e", "f", 5, b"bytes"]

    def test_add_a_listing(self) -> None:
        listing = camina.Listing([1])
        listing.add(camina.Listing([2, 3]))
        assert listing.contents == [1, 2, 3]

    def test_delete(self) -> None:
        listing = camina.Listing([1, 2, 3, 4])
        listing.delete(0)
        assert listing.contents == [2, 3, 4]
        del listing[-1]
        assert listing.contents == [2, 3]
        del listing[0:1]
        assert listing.contents == [3]
        with pytest.raises(IndexError):
            listing.delete(10)

    def test_prepend(self) -> None:
        listing = camina.Listing([3])
        listing.prepend(2)
        listing.prepend(["a", "b"])
        listing.prepend("xy")
        assert listing.contents == ["xy", "a", "b", 2, 3]

    def test_operators(self) -> None:
        listing = camina.Listing([1])
        combined = listing + [2, 3]
        assert combined.contents == [1, 2, 3]
        assert listing.contents == [1]
        listing += 4
        assert listing.contents == [1, 4]

    def test_slicing_and_setting(self) -> None:
        listing = camina.Listing([1, 2, 3, 4])
        piece = listing[1:3]
        assert isinstance(piece, camina.Listing)
        assert piece.contents == [2, 3]
        listing[0] = 10
        listing[1:3] = [20, 30]
        assert listing.contents == [10, 20, 30, 4]

    def test_subset_include_only(self) -> None:
        listing = camina.Listing(["a", "b", "c"])
        assert listing.subset(include="a").contents == ["a"]
        assert listing.subset(include=["c", "a"]).contents == ["a", "c"]

    def test_subset_exclude_only(self) -> None:
        listing = camina.Listing(["a", "b", "c"])
        assert listing.subset(exclude=["a", "c"]).contents == ["b"]

    def test_subset_requires_argument(self) -> None:
        with pytest.raises(ValueError, match="must not be None"):
            camina.Listing(["a"]).subset()

    def test_subset_leaves_original(self) -> None:
        listing = camina.Listing(["a", "b"])
        subset = listing.subset(include="a")
        subset.append("z")
        assert listing.contents == ["a", "b"]

    def test_sequence_interface(self) -> None:
        listing = camina.Listing([3, 1, 2])
        assert len(listing) == 3
        assert 2 in listing
        assert list(listing) == [3, 1, 2]
        assert list(reversed(listing)) == [2, 1, 3]
        assert listing.index(1) == 1
        assert listing.count(3) == 1
        assert listing.pop() == 2
        listing.reverse()
        assert listing.contents == [1, 3]


class TestHybrid:
    def test_basic_operations(self) -> None:
        hybrid = camina.Hybrid(contents=["a", "b", "c"])
        hybrid.setdefault(value="No")
        assert hybrid.get("tree") == "No"
        assert hybrid[1] == "b"
        hybrid.add(item="d")
        assert hybrid[3] == "d"
        hybrid.insert(2, "zebra")
        assert hybrid[2] == "zebra"
        sub_hybrid = hybrid.subset(
            include=["a", "b", "c", "d", "zebra"], exclude="d"
        )
        assert sub_hybrid.contents == ["a", "b", "zebra", "c"]
        sub_hybrid.remove("c")
        assert sub_hybrid.contents == ["a", "b", "zebra"]
        assert hybrid[0] == "a"
        assert hybrid["zebra"] == "zebra"
        hybrid.append("b")
        assert hybrid.values() == ("a", "b", "zebra", "c", "d", "b")
        assert hybrid.keys() == ("a", "b", "zebra", "c", "d", "b")
        hybrid.remove("b")
        assert hybrid.contents == ["a", "zebra", "c", "d", "b"]
        hybrid.clear()
        test_class = Sample()
        hybrid.add(test_class)
        assert hybrid.keys() == ("something",)
        assert hybrid.values() == (test_class,)

    def test_getitem_by_name(self) -> None:
        one, two = Sample("one"), Sample("two")
        hybrid = camina.Hybrid([one, two])
        assert hybrid["one"] is one
        assert hybrid[1] is two
        assert hybrid[-1] is two
        with pytest.raises(KeyError, match="not in Hybrid"):
            hybrid["three"]

    def test_duplicate_names_return_a_hybrid(self) -> None:
        first, second, other = Sample("same"), Sample("same"), Sample("other")
        hybrid = camina.Hybrid([first, other, second])
        result = hybrid["same"]
        assert isinstance(result, camina.Hybrid)
        assert result.contents == [first, second]

    def test_slice(self) -> None:
        hybrid = camina.Hybrid(["a", "b", "c"])
        piece = hybrid[1:]
        assert isinstance(piece, camina.Hybrid)
        assert piece.contents == ["b", "c"]

    def test_get(self) -> None:
        hybrid = camina.Hybrid(["a"], default_factory=list)
        assert hybrid.get("a") == "a"
        assert hybrid.get("missing") == []
        assert hybrid.get(10) == []
        assert hybrid.get("missing", "explicit") == "explicit"
        with pytest.raises(KeyError, match="not in the Hybrid"):
            camina.Hybrid().get("missing")

    def test_setdefault_dict_behavior(self) -> None:
        hybrid = camina.Hybrid(["a"])
        assert hybrid.setdefault("a", "ignored") == "a"
        assert hybrid.setdefault("b", "b") == "b"
        assert hybrid.contents == ["a", "b"]
        with pytest.raises(TypeError, match="key or a value"):
            hybrid.setdefault()

    def test_delete(self) -> None:
        hybrid = camina.Hybrid(["a", "b", "a", "c"])
        hybrid.delete(1)
        assert hybrid.contents == ["a", "a", "c"]
        hybrid.delete("a")
        assert hybrid.contents == ["c"]
        with pytest.raises(KeyError, match="not in Hybrid"):
            hybrid.delete("missing")
        del hybrid["c"]
        assert hybrid.contents == []

    def test_delete_by_name_of_object(self) -> None:
        hybrid = camina.Hybrid([Sample("x"), Sample("y")])
        hybrid.delete("x")
        assert hybrid.keys() == ("y",)

    def test_items_and_update(self) -> None:
        hybrid = camina.Hybrid(["a"])
        hybrid.update({"ignored": "b", "also_ignored": "c"})
        assert hybrid.items() == (("a", "a"), ("b", "b"), ("c", "c"))

    def test_contains(self) -> None:
        sample = Sample("named")
        hybrid = camina.Hybrid(["a", sample])
        assert "a" in hybrid
        assert sample in hybrid
        assert "named" in hybrid
        assert "missing" not in hybrid

    def test_setitem(self) -> None:
        hybrid = camina.Hybrid(["a", "b", "c"])
        hybrid[0] = "z"
        hybrid["ignored"] = "d"
        hybrid[1:3] = ["x", "y"]
        assert hybrid.contents == ["z", "x", "y", "d"]

    def test_subset_by_name(self) -> None:
        hybrid = camina.Hybrid([Sample("one"), Sample("two"), Sample("three")])
        assert hybrid.subset(include=["one", "three"]).keys() == (
            "one",
            "three",
        )
        assert hybrid.subset(exclude="two").keys() == ("one", "three")

    def test_unhashable_items_need_a_name(self) -> None:
        hybrid = camina.Hybrid()
        hybrid.add(Sample())  # dataclasses with eq are unhashable but named
        with pytest.raises(TypeError, match="hashable or have a name"):
            hybrid.add([[1, 2]])
        with pytest.raises(TypeError, match="hashable or have a name"):
            hybrid.append({"a": 1})
        with pytest.raises(TypeError, match="hashable or have a name"):
            hybrid.insert(0, [1])
        with pytest.raises(TypeError, match="hashable or have a name"):
            hybrid[0] = [1]
        with pytest.raises(TypeError, match="hashable or have a name"):
            hybrid[0:1] = [[1]]
        with pytest.raises(TypeError, match="hashable or have a name"):
            camina.Hybrid(contents=[[1]])
        assert len(hybrid) == 1

    def test_operators(self) -> None:
        hybrid = camina.Hybrid(["a"])
        assert (hybrid + ["b"]).contents == ["a", "b"]
        hybrid += "c"
        assert hybrid.contents == ["a", "c"]
