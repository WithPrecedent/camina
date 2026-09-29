"""Tests for `camina.mapping`."""

from __future__ import annotations

import collections
import dataclasses

import pytest

import camina


@dataclasses.dataclass
class Sample:
    name: str = "something"


@dataclasses.dataclass
class Another:
    name: str = "another"


@dataclasses.dataclass
class Third:
    name: str = "third"


class TestDictionary:
    def test_fromkeys(self) -> None:
        created = camina.Dictionary.fromkeys(keys=["a", "b", "c"], value="tree")
        assert created["a"] == "tree"
        assert created.keys() == ("a", "b", "c")
        assert camina.Dictionary.fromkeys(["a"]).contents == {"a": None}
        with_default = camina.Dictionary.fromkeys(["a"], 1, default_factory=5)
        assert with_default.default_factory == 5

    def test_get_and_default(self) -> None:
        dictionary = camina.Dictionary(
            contents={"a": "b", "c": "d"}, default_factory="Nada"
        )
        assert dictionary.get("f") == "Nada"
        assert dictionary["a"] == "b"
        assert dictionary.get("a") == "b"
        assert dictionary.get("f", "explicit") == "explicit"

    def test_get_callable_default(self) -> None:
        dictionary = camina.Dictionary(default_factory=list)
        assert dictionary.get("missing") == []
        assert dictionary.get("missing") is not dictionary.get("missing")

    def test_get_raises_without_default(self) -> None:
        with pytest.raises(KeyError, match="not in the Dictionary"):
            camina.Dictionary().get("missing")

    def test_get_unhashable_key(self) -> None:
        assert camina.Dictionary(default_factory=1).get([1]) == 1

    def test_setdefault_value(self) -> None:
        dictionary = camina.Dictionary()
        assert dictionary.setdefault(value="No") is None
        assert dictionary.get("missing") == "No"

    def test_setdefault_dict_behavior(self) -> None:
        dictionary = camina.Dictionary({"a": 1})
        assert dictionary.setdefault("a", 5) == 1
        assert dictionary.setdefault("b", 5) == 5
        assert dictionary.setdefault("c") is None
        assert dictionary.contents == {"a": 1, "b": 5, "c": None}
        with pytest.raises(TypeError, match="key or a value"):
            dictionary.setdefault()

    def test_add_and_delete(self) -> None:
        dictionary = camina.Dictionary(contents={"a": "b"})
        dictionary.add({"e": "f"})
        assert dictionary["e"] == "f"
        dictionary.add({"g": "h"}, i="j")
        assert dictionary["i"] == "j"
        dictionary.delete("e")
        assert "e" not in dictionary
        del dictionary["g"]
        assert "g" not in dictionary
        with pytest.raises(KeyError):
            dictionary.delete("missing")

    def test_operators(self) -> None:
        dictionary = camina.Dictionary({"a": 1})
        combined = dictionary + {"b": 2}
        assert combined.contents == {"a": 1, "b": 2}
        assert dictionary.contents == {"a": 1}
        dictionary += camina.Dictionary({"c": 3})
        assert dictionary.contents == {"a": 1, "c": 3}

    def test_views_are_tuples(self) -> None:
        dictionary = camina.Dictionary({"a": 1, "b": 2})
        assert dictionary.keys() == ("a", "b")
        assert dictionary.values() == (1, 2)
        assert dictionary.items() == (("a", 1), ("b", 2))

    def test_mutable_mapping_interface(self) -> None:
        dictionary = camina.Dictionary({"a": 1, "b": 2})
        dictionary["c"] = 3
        assert len(dictionary) == 3
        assert list(dictionary) == ["a", "b", "c"]
        assert dictionary.pop("a") == 1
        dictionary.update({"d": 4})
        assert dictionary.popitem() == ("d", 4)
        dictionary.clear()
        assert len(dictionary) == 0
        with pytest.raises(KeyError, match="empty"):
            dictionary.popitem()

    def test_subset(self) -> None:
        dictionary = camina.Dictionary(
            contents={"a": "b", "c": "d", "e": "f"}, default_factory="x"
        )
        subset = dictionary.subset(include=["a", "e"])
        assert "a" in subset.keys()
        assert "b" not in subset.keys()
        assert "a" not in subset.values()
        assert "b" in subset.values()
        assert subset.default_factory == "x"
        assert len(dictionary) == 3

    def test_subset_exclude_and_both(self) -> None:
        dictionary = camina.Dictionary({"a": 1, "b": 2, "c": 3})
        assert dictionary.subset(exclude="a").contents == {"b": 2, "c": 3}
        assert dictionary.subset("a", "b").contents == {"a": 1}
        assert dictionary.subset(
            include=["a", "b"], exclude=["b"]
        ).contents == {"a": 1}
        assert dictionary.subset(include="missing").contents == {}

    def test_subset_requires_argument(self) -> None:
        with pytest.raises(ValueError, match="must not be None"):
            camina.Dictionary({"a": 1}).subset()

    def test_subset_does_not_share_containers(self) -> None:
        dictionary = camina.Dictionary({"a": 1})
        subset = dictionary.subset(include="a")
        subset["b"] = 2
        assert "b" not in dictionary


class TestCatalog:
    def test_wildcards(self) -> None:
        catalog = camina.Catalog(contents={"tester": Sample})
        catalog.add({"another": Another})
        catalog.add({"a_third": Third()})
        assert "tester" in catalog
        assert "another" in catalog
        assert "a_third" in catalog
        assert catalog["all"] == catalog["default"]
        assert catalog["None"] is None
        catalog.default = "tester"
        assert catalog["default"] == catalog["tester"]
        del catalog[["tester", "another"]]
        assert "tester" not in catalog
        assert len(catalog) == 1

    def test_all_and_default_variants(self) -> None:
        catalog = camina.Catalog(contents={"a": 1, "b": 2})
        assert catalog["all"] == [1, 2]
        assert catalog["All"] == [1, 2]
        assert catalog[["all"]] == [1, 2]
        assert catalog["defaults"] == [1, 2]
        catalog.default = ["a"]
        assert catalog["Default"] == [1]
        assert catalog[["default"]] == [1]

    def test_recursive_default_is_all(self) -> None:
        catalog = camina.Catalog(contents={"a": 1}, default="default")
        assert catalog["default"] == [1]

    def test_none(self) -> None:
        assert camina.Catalog()["none"] is None
        assert camina.Catalog(always_return_list=True)["none"] == []
        assert camina.Catalog(default_factory="dflt")["none"] == "dflt"
        assert camina.Catalog(default_factory=list)[["None"]] == []

    def test_list_of_keys(self) -> None:
        catalog = camina.Catalog(contents={"a": 1, "b": 2, "c": 3})
        assert catalog[["a", "c"]] == [1, 3]
        assert catalog[("a", "b")] == [1, 2]
        assert catalog[["a", "missing"]] == [1]

    def test_tuple_key_stored_in_catalog(self) -> None:
        catalog = camina.Catalog(contents={("a", "b"): "pair", "a": 1})
        assert catalog[("a", "b")] == "pair"

    def test_always_return_list(self) -> None:
        catalog = camina.Catalog(contents={"a": 1}, always_return_list=True)
        assert catalog["a"] == [1]

    def test_missing_key(self) -> None:
        with pytest.raises(KeyError, match="not in Catalog"):
            camina.Catalog()["missing"]
        assert camina.Catalog(default_factory=3).get("missing") == 3

    def test_set_multiple_keys(self) -> None:
        catalog = camina.Catalog()
        catalog["a"] = 1
        catalog[["b", "c"]] = [2, 3]
        assert catalog.contents == {"a": 1, "b": 2, "c": 3}

    def test_set_unhashable_key_that_is_not_a_sequence(self) -> None:
        with pytest.raises(TypeError):
            camina.Catalog()[{"a"}] = 1

    def test_delete(self) -> None:
        catalog = camina.Catalog(contents={"a": 1, "b": 2, "c": 3})
        catalog.delete("a")
        assert "a" not in catalog
        catalog.delete(["b", "c"])
        assert len(catalog) == 0

    def test_delete_missing_key_keeps_others(self) -> None:
        catalog = camina.Catalog(contents={"a": 1})
        with pytest.raises(KeyError, match="not found in the Catalog"):
            catalog.delete(["a", "missing"])
        assert "a" in catalog

    def test_delete_does_not_replace_contents(self) -> None:
        contents = {"a": 1, "b": 2}
        catalog = camina.Catalog(contents=contents)
        catalog.delete("a")
        assert contents == {"b": 2}

    def test_wildcard_words_are_not_deleted(self) -> None:
        catalog = camina.Catalog(contents={"a": 1})
        with pytest.raises(KeyError):
            catalog.delete("all")


class TestChainDictionary:
    @pytest.fixture
    def chain(self) -> camina.ChainDictionary:
        return camina.ChainDictionary(
            contents=[
                camina.Dictionary({"a": 1, "b": 2}),
                camina.Dictionary({"b": 20, "c": 30}),
            ]
        )

    def test_getitem_first_match(self, chain: camina.ChainDictionary) -> None:
        assert chain["a"] == 1
        assert chain["b"] == 2
        assert chain["c"] == 30
        with pytest.raises(KeyError, match="not found"):
            chain["missing"]

    def test_getitem_all_matches(self, chain: camina.ChainDictionary) -> None:
        chain.return_first = False
        assert chain["b"] == [2, 20]
        assert chain["a"] == 1
        with pytest.raises(KeyError):
            chain["missing"]

    def test_unique_keys_values_items(
        self, chain: camina.ChainDictionary
    ) -> None:
        assert chain.keys() == ("a", "b", "c")
        assert chain.values() == (1, 2, 30)
        assert chain.items() == (("a", 1), ("b", 2), ("c", 30))
        assert list(chain) == ["a", "b", "c"]
        assert len(chain) == 3
        assert dict(chain) == {"a": 1, "b": 2, "c": 30}

    def test_contains(self, chain: camina.ChainDictionary) -> None:
        assert "c" in chain
        assert "z" not in chain

    def test_get(self, chain: camina.ChainDictionary) -> None:
        assert chain.get("c") == 30
        assert chain.get("z", "d") == "d"
        with pytest.raises(KeyError):
            chain.get("z")

    def test_setitem(self, chain: camina.ChainDictionary) -> None:
        chain["b"] = 200
        chain["d"] = 4
        assert chain.contents[0].contents == {"a": 1, "b": 200, "d": 4}
        assert chain.contents[1].contents == {"b": 20, "c": 30}

    def test_setitem_on_empty(self) -> None:
        chain = camina.ChainDictionary()
        chain["a"] = 1
        assert chain["a"] == 1
        assert len(chain.contents) == 1

    def test_add(self, chain: camina.ChainDictionary) -> None:
        chain.add({"z": 26})
        assert chain["z"] == 26
        assert len(chain.contents) == 3
        with pytest.raises(TypeError, match="MutableMapping"):
            chain.add("nope")  # type: ignore[arg-type]

    def test_delete(self, chain: camina.ChainDictionary) -> None:
        chain.delete("b")
        assert "b" not in chain
        del chain["a"]
        assert chain.keys() == ("c",)
        with pytest.raises(KeyError, match="not found"):
            chain.delete("missing")

    def test_new_child_and_parents(self, chain: camina.ChainDictionary) -> None:
        chain.new_child({"a": 100})
        assert chain["a"] == 100
        chain.new_child(x=1)
        assert chain["x"] == 1
        assert len(chain.contents) == 4
        parents = chain.parents
        assert len(parents.contents) == 3
        assert parents["a"] == 100
        assert "x" not in parents
        assert isinstance(parents, camina.ChainDictionary)

    def test_maps_property(self, chain: camina.ChainDictionary) -> None:
        assert chain.maps is chain.contents
        chain.maps = [camina.Dictionary({"q": 1})]
        assert chain.keys() == ("q",)
        del chain.maps
        assert chain.contents == []

    def test_subset(self, chain: camina.ChainDictionary) -> None:
        subset = chain.subset(include=["a", "c"])
        assert subset.keys() == ("a", "c")
        assert subset.return_first is True
        excluded = chain.subset(exclude="b")
        assert excluded.keys() == ("a", "c")
        assert chain.keys() == ("a", "b", "c")
        with pytest.raises(ValueError, match="must not be None"):
            chain.subset()

    def test_fromkeys(self) -> None:
        chain = camina.ChainDictionary.fromkeys(
            ["a", "b"], 0, return_first=False
        )
        assert chain.keys() == ("a", "b")
        assert chain.return_first is False
        assert len(chain.contents) == 1

    def test_plain_dicts_are_supported(self) -> None:
        chain = camina.ChainDictionary(contents=[{"a": 1}, {"b": 2}])
        assert chain["b"] == 2
        assert chain.subset(include="a").keys() == ("a",)


class TestRepository:
    def test_add_and_delete(self) -> None:
        repository = camina.Repository()
        repository.add(Another())
        repository.add(Third, "random_name")
        assert "another" in repository
        assert "random_name" in repository
        repository.delete("random_name")
        assert "random_name" not in repository

    def test_unique_keys(self) -> None:
        repository = camina.Repository()
        repository.add(Another())
        repository.add(Another())
        repository.add(Another())
        assert repository.keys() == ("another", "another2", "another3")

    def test_explicit_keys_are_also_made_unique(self) -> None:
        repository = camina.Repository()
        repository.add(1, "one")
        repository.add(2, "one")
        assert repository.contents == {"one": 1, "one2": 2}

    def test_overwrite(self) -> None:
        repository = camina.Repository(overwrite=True)
        first, second = Another(), Another()
        repository.add(first)
        repository.add(second)
        assert len(repository) == 1
        assert repository["another"] is second

    def test_inferred_names(self) -> None:
        repository = camina.Repository()
        repository.add(Sample)
        repository.add(collections.OrderedDict())
        repository.add("text")
        assert repository.keys() == ("sample", "ordered_dict", "text")

    def test_get_name_can_be_overridden(self) -> None:
        class Shouting(camina.Repository):
            def _get_name(self, item: object) -> str:
                return str(item).upper()

        repository = Shouting()
        repository.add("quiet")
        assert repository.keys() == ("QUIET",)

    def test_operators(self) -> None:
        repository = camina.Repository()
        repository += Another()
        repository += Another()
        assert repository.keys() == ("another", "another2")
