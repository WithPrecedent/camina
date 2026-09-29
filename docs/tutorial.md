# Tutorial

This tutorial walks through the main parts of `camina`: converters, modifiers, names, and timing tools. Every example is a
complete session that you can paste into a Python prompt.

## Installation

```sh
pip install camina
```

`camina` requires Python 3.11 or later and has no dependencies.

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

## Naming things

`camina.namify` returns a name for a str, an object with a `name` attribute, a
class, or a function:

```python
camina.namify("already")        # 'already'
camina.namify(dict)             # 'dict'
camina.namify(camina.namify)    # 'namify'
```

## Timing and timestamps

```python
@camina.timer
def work():
    ...

work()      # prints "work completed in 0:00:00"
camina.how_soon_is_now(prefix="run_")   # 'run_2024-01-31_14-05'
```

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
  your own types and how naming works.
* The [Recipes](recipes.md) page shows short solutions to common tasks.
* The API reference documents every function, including their
  argument and return types.
