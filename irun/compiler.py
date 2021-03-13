@singledispatch
def compile(node):
    raise ValueError(f"Unsupported node: {type(node).__name__}")
