# Tutorial

This tutorial walks through the main parts of `camina`. Every example is a
complete session that you can paste into a Python prompt.

## Installation

```sh
pip install camina
```

`camina` requires Python 3.11 or later and has no dependencies.

## The shared interface

The containers in `camina` (`Dictionary`, `Catalog`, `ChainDictionary`,
`Repository`, `Listing`, and `Hybrid`) all inherit from `Bunch`. A `Bunch`
stores its data in a `contents` attribute and requires three methods:

* `add`: the default way to put something into the container.
* `delete`: the default way to take something out.
* `subset`: returns a new container of the same type with only some of the data.

The `+` operator returns a copy with the other item added, and `+=` adds the
item in place. Both call `add`.

```python
import camina

dictionary = camina.Dictionary({"a": 1, "b": 2})
dictionary.add({"c": 3})            # like dict.update
dictionary.delete("b")              # like del dictionary["b"]
only_a = dictionary.subset(include="a")

bigger = dictionary + {"d": 4}      # dictionary is unchanged
dictionary += {"e": 5}              # dictionary is changed
```

## Working with mappings

### Dictionary

`Dictionary` is a `dict` replacement. Its `keys()`, `values()`, and `items()`
methods return tuples, and its `get` method uses a default value (or a callable
that creates one) when a key is missing:

```python
options = camina.Dictionary({"depth": 3}, default_factory=list)
options.get("width")        # []
options.setdefault(value=10)
options.get("width")        # 10
```

If there is no default and no `default` argument, `get` raises a `KeyError`.
The `setdefault` method also works like `dict.setdefault` when it is passed a
key.

### Catalog

A `Catalog` is meant for storing options and strategies. Besides ordinary keys,
it understands three wildcards and lists of keys:

```python
catalog = camina.Catalog({"linear": "LinearModel", "tree": "TreeModel"})
catalog["linear"]                   # 'LinearModel'
catalog["all"]                      # ['LinearModel', 'TreeModel']
catalog[["tree", "missing"]]        # ['TreeModel'] (missing keys are skipped)
catalog.default = "tree"
catalog["default"]                  # 'TreeModel'
catalog["none"]                     # None
```

Set `always_return_list=True` if you want every lookup to return a list, which
makes iterating over the result simpler.

### ChainDictionary

A `ChainDictionary` looks up keys in several mappings in order, like
`collections.ChainMap`:

```python
defaults = {"color": "red", "size": 1}
overrides = {"color": "blue"}
chain = camina.ChainDictionary([overrides, defaults])
chain["color"]      # 'blue'
chain["size"]       # 1
chain.keys()        # ('color', 'size')
chain.new_child({"color": "green"})
chain["color"]      # 'green'
```

Assigning a value stores it in the first mapping. With `return_first=False`,
`chain["color"]` returns a list of every match instead.

### Repository

A `Repository` chooses keys for the items you add, using `camina.namify`:

```python
repository = camina.Repository()
repository.add(camina.Dictionary())
repository.add(camina.Dictionary())
repository.keys()       # ('dictionary', 'dictionary2')
```

By default it never overwrites an item. Pass `overwrite=True` to replace items
with the same inferred key. You can also pass your own key:
`repository.add(item, key="name")`.

## Working with sequences

### Listing

A `Listing` is a `list` whose `add` method extends with sequences (but not
strings) and appends anything else. It also has a `prepend` method:

```python
listing = camina.Listing(["b"])
listing.add(["c", "d"])
listing.prepend("a")
listing.contents        # ['a', 'b', 'c', 'd']
listing.subset(exclude="d").contents    # ['a', 'b', 'c']
```

### Hybrid

A `Hybrid` is a list that can also be used like a dictionary. Items are found
by index or by name. The name of an item is its `name` attribute, or the item
itself if it has none. Names can repeat; when they do, a `Hybrid` of the
matches is returned:

```python
import dataclasses

@dataclasses.dataclass
class Step:
    name: str

steps = camina.Hybrid([Step("load"), Step("clean"), Step("clean")])
steps[0]                # Step(name='load')
steps["load"]           # Step(name='load')
steps["clean"]          # Hybrid of both 'clean' steps
steps.keys()            # ('load', 'clean', 'clean')
```

A `Hybrid` only accepts items that are hashable or that have a `name`
attribute that is a str. Avoid storing `int` values in one, since `hybrid[3]`
always means "the item at index 3".

## Wrapping objects

A `Proxy` forwards attribute access, item access, calls, and `in` checks to the
object it wraps. Setting an attribute changes the wrapped object unless the
proxy itself already has that attribute:

```python
@dataclasses.dataclass
class Settings:
    name: str = "default"

settings = Settings()
proxy = camina.Proxy(settings)
proxy.name = "custom"
settings.name           # 'custom'
```

## Converting types

The converters make functions that accept "one or many" arguments easy to write:

```python
camina.listify("a")             # ['a']
camina.listify(("a", "b"))      # ['a', 'b']
camina.tuplify(["a", "b"])      # ('a', 'b')
camina.iterify("abc")           # ('abc',) (strings are not iterated)
camina.numify("3.5")            # 3.5
camina.typify("1, 2, yes")      # [1, 2, True]
camina.pathlibify("data/file.csv")
```

`camina.windowify` slides a window over any iterable, and `camina.kwargify`
turns positional arguments into keyword arguments using a class's annotations
or dataclass fields.

## Modifying strings and collections

The modifiers work on `str`, `dict` (keys), `list`, `set`, and `tuple` values
and return a new object of the same type:

```python
camina.add_prefix(["a", "b"], "my", divider="_")     # ['my_a', 'my_b']
camina.drop_suffix({"a_id": 1}, "id", divider="_")   # {'a': 1}
camina.drop_privates(["_x", "y"])                    # ['y']
camina.deduplicate([1, 2, 1])                        # [1, 2]
camina.snakify("HTTPResponse")                       # 'http_response'
camina.capitalify("http_response")                   # 'HttpResponse'
camina.cleave("a_b_c")                               # ('a_b', 'c')
camina.uniquify("name", {"name": 1})                 # 'name2'
```

## Next steps

* The [Advanced User Guide](advanced.md) explains how to extend `camina` with
  your own types and how to customize naming.
* The [Recipes](recipes.md) page shows short solutions to common tasks.
* The API reference documents every class and function, including their
  argument and return types.
