# IRUN: Indulgent Reiz User Notation

A human-friendly query language (python-like DSL) for generating
[Reiz QL](https://github.com/reizio/reiz.io/blob/master/docs/reizql.md) queries.

```py
with open(...) as $stream:
    tree = ast.parse($stream.read())
```

The query above would match all of these potential cases (via [Reiz](https://github.com/reizio/reiz.io)):
```py
with open('somefile.py') as file_s:
    tree = ast.parse(file_s.read())

with open(some_path) as stream:
    tree = ast.parse(stream.read())

with open(pathlib_path / 'file.py') as s_file:
    tree = ast.parse(s_file.read())
```

and filter out the rest (stuff like this):
```py
with open(pathlib_path / 'file.py', encoding='x') as stream:
    tree = ast.parse(stream.read())

with open() as stream:
    tree = ast.parse(stream.read())

with foo(path) as stream:
    tree = ast.parse(stream.read())

with open(path) as stream:
    tree = ast.parse(other_stream.read())

with open(path) as stream:
    tree = ast.foo(stream.read())

with open(path) as stream:
    tree = bar.parse(stream.read())

with open(path) as stream:
    tree = bar.baz(stream.read())

with open(path) as xxx:
    tree = ast.parse(yyy.read())

with open(path) as xxx:
    zzz = ast.parse(xxx.read())
```
