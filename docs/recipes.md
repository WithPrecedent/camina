# Recipes

Short solutions to common tasks. See the [Tutorial](tutorial.md) for the basics.

## Accept one item or many

```python
import camina


def load(paths):
    return [camina.pathlibify(p) for p in camina.listify(paths)]


load("a.csv")               # [Path('a.csv')]
load(["a.csv", "b.csv"])    # [Path('a.csv'), Path('b.csv')]
```

## Register strategies by name and pick a default

```python
strategies = camina.Catalog(
    {"fast": fast_strategy, "safe": safe_strategy}, default="safe")

strategies["default"]         # safe_strategy
strategies[["fast", "safe"]]  # [fast_strategy, safe_strategy]
```

## Collect objects without choosing keys

```python
plugins = camina.Repository()
plugins.add(MyPlugin())                 # key: 'my_plugin'
plugins.add(MyPlugin())                 # key: 'my_plugin2'
plugins.add(OtherPlugin(), key="other")
```

## Layer configuration

```python
config = camina.ChainDictionary([cli_options, file_options, defaults])
config["timeout"]   # the first value found, in that order
```

## Keep order and allow repeated names

```python
pipeline = camina.Hybrid([Step("load"), Step("clean"), Step("clean")])
pipeline["clean"]   # both 'clean' steps in a Hybrid
pipeline[0]         # the first step
pipeline.remove(pipeline[1])   # removes the first step equal to that one
```

## Namespace keys

```python
camina.add_prefix({"size": 1, "color": 2}, "widget", divider="_")
# {'widget_size': 1, 'widget_color': 2}

camina.drop_prefix({"widget_size": 1}, "widget", divider="_")
# {'size': 1}
```

## List the public attributes of an object

```python
camina.drop_privates(dir(obj))      # no names that start with an underscore
camina.drop_dunders(dir(obj))       # keeps single-underscore names
```

## Parse settings that arrive as strings

```python
{k: camina.typify(v) for k, v in {"n": "3", "debug": "yes", "ids": "1, 2"}.items()}
# {'n': 3, 'debug': True, 'ids': [1, 2]}
```

## Compare neighbors in a sequence

```python
for before, after in camina.windowify([1, 4, 9, 16], length=2):
    print(after - before)       # 3, 5, 7
```

## Make a dataclass use less memory

```python
@dataclasses.dataclass
class Point:
    x: float = 0.0
    y: float = 0.0

Point = camina.add_slots(Point)   # instances no longer have a __dict__
```

Note that the zero-argument form of `super()` does not work inside methods of
a class returned by `add_slots`. Alternatively, use
`dataclass(slots=True)`.

## Time a function

```python
@camina.timer
def train():
    ...

train()     # prints "train completed in 0:00:12" and returns the result
```

## Create timestamped names

```python
camina.how_soon_is_now(prefix="report_")    # 'report_2024-01-31_14-05'
```
