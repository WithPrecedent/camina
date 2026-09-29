# Advanced User Guide

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
returned instead. The originals are never changed.

## Naming

`camina.namify` creates a name for anything:

1. A `str` is its own name.
2. An instance with a `name` attribute that is a `str` uses that attribute.
3. Anything with a `__name__` (classes and functions) uses it, converted to
   snake case.
4. Otherwise the snake case name of the item's class is used.

If none of these produce a name, the `default` argument is returned.

## Specific converters

Besides the general converters, `camina.convert` has single-purpose functions
named `to_{output type}` and `{input type}_to_{output type}`. The `to_*`
functions dispatch on the type of the item, and the others are registered with
them:

```python
from camina import convert

convert.to_float("3.5")             # 3.5
convert.to_float(3)                 # 3.0
convert.to_list("[1, 2]")           # [1, 2]
convert.to_str(["a", 1])            # 'a, 1'
convert.to_index(4.0)               # 4
convert.str_to_path("a/b")          # PosixPath('a/b')
```

Register your own conversions the same way:
`@convert.to_str.register(MyType)`.

## Defaults for missing input

`listify`, `tuplify`, and `stringify` accept a `default` for `None` input. Because
`None` itself is ambiguous as a default, pass the string `"None"` if you want `None`
returned:

```python
camina.listify(None)                    # []
camina.listify(None, default=["x"])     # ['x']
camina.listify(None, default="None")    # None
```

## Typing

`camina` is fully annotated and checked with `mypy`. The dispatchers are typed
with `Any` because they accept many types, but the type-specific functions
(for example, `add_prefix_to_list`) have precise signatures.
