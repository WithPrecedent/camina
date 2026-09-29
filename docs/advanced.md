# Advanced User Guide

## Building your own container

To create a container with the same interface as the others in `camina`,
subclass `camina.Bunch` and implement `add`, `delete`, and `subset`. `Bunch`
is a dataclass, so the container's data lives in the `contents` field:

```python
import dataclasses
from typing import Any

import camina


@dataclasses.dataclass
class Bag(camina.Bunch):
    """Unordered collection that allows repeated items."""

    contents: list[Any] = dataclasses.field(default_factory=list)

    def add(self, item: Any) -> None:
        self.contents.append(item)

    def delete(self, item: Any) -> None:
        self.contents.remove(item)

    def subset(self, include: Any = None, exclude: Any = None) -> "Bag":
        kept = [i for i in self.contents if i != exclude]
        return dataclasses.replace(self, contents=kept)


bag = Bag(["a"])
bag += "b"          # calls bag.add("b") in place
bigger = bag + "c"  # copy with "c" added
```

`Bunch` supplies `+`, `+=`, `del bunch[item]`, `in`, `len`, and iteration.
`Dictionary` and `Listing` also mix in `MutableMapping` and `MutableSequence`,
which is why they have the full dict and list interfaces.

## Extending the converters and modifiers

Most converters and modifiers are `functools.singledispatch` functions. You can
register support for another type with the `register` method of the function:

```python
import camina


class Tags(list):
    """A list of str tags."""


@camina.add_prefix.register(Tags)
def add_prefix_to_tags(item, /, prefix, divider="", recursive=False):
    return Tags(camina.add_prefix(list(item), prefix, divider))


camina.add_prefix(Tags(["a"]), "x")     # Tags(['xa'])
```

The type-specific functions are also available on their own when you know the
type in advance (for example, `camina.add_prefix_to_list`).

Modifiers keep the type of what they modify. A `dict` subclass, an
`OrderedDict`, and a `defaultdict` all come back as themselves. If a container
type cannot be recreated from a dict or list, a plain `dict` or `list` is
returned instead.

## Naming and keys

`camina.namify` creates a name for anything:

1. A `str` is its own name.
2. An instance with a `name` attribute that is a `str` uses that attribute.
3. Anything with a `__name__` (classes and functions) uses it, converted to
   snake case.
4. Otherwise the snake case name of the item's class is used.

`Repository`, `Hybrid`, and the `Name` descriptor all use the *key namer*, a
global function that defaults to `namify`. Replace it for your whole program
with `set_key_namer`, and restore the default by passing `None`:

```python
camina.set_key_namer(lambda item: type(item).__name__.lower())
camina.get_key_namer()      # your function
camina.set_key_namer(None)  # back to camina.namify
```

To change how only one `Repository` names items, subclass it and override
`_get_name`. `set_method_namer` and `get_method_namer` do the same for the names
of factory methods (by default, `"from_" + namify(item)`).

### The Name descriptor

`Name` gives a class a `name` attribute that is inferred until one is stored. It
works in ordinary classes and as a dataclass field default:

```python
import dataclasses


@dataclasses.dataclass
class Widget:
    name: str = camina.Name()


Widget().name           # 'widget'
Widget(name="a").name   # 'a'
```

Pass `namer=` to `Name` to use a different function for one attribute. The
function receives the class that owns the descriptor.

## Writing descriptors

`camina.Descriptor` is a base class that stores a value on the owning instance
under the descriptor's name with a leading underscore. Subclass it and override
`__set__` to validate values:

```python
class Positive(camina.Descriptor):
    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"{self.attribute_name} must be positive")
        super().__set__(instance, value)


class Box:
    width = Positive()
```

`Descriptor` provides `attribute_name`, `private_name`, and `owner` through
`__set_name__`, and returns the descriptor itself when accessed on the class.

## Defaults

`default_factory` on `Dictionary`, `Catalog`, `ChainDictionary`, `Repository`,
and `Hybrid` can be a value or a callable. If it is callable, it is called each
time a default is needed. That is handled by `camina.resolve_default`. To store
a callable as a *value*, wrap it (for example, in a `functools.partial` that
returns it).

## Performance notes

* `Hybrid` looks up names by scanning its list. It trades lookup speed for
  flexibility, so prefer `Dictionary` or `Repository` when you will make many
  lookups.
* `Catalog` compares keys against its wildcards on every lookup. That cost is
  small but nonzero.
* Modifiers create new containers instead of changing the ones passed in.

## Typing

`camina` is fully annotated and checked with `mypy`. The container types are
not generic, so annotate their contents with the standard collection types
(for example, `Dictionary` stores a `MutableMapping[Hashable, Any]`).
