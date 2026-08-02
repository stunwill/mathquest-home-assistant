import ast
from pathlib import Path


def test_main_imports_sqlalchemy_func():
    source = Path(__file__).parents[1] / 'app' / 'main.py'
    tree = ast.parse(source.read_text())
    sqlalchemy_imports = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module == 'sqlalchemy'
        for alias in node.names
    }
    assert 'func' in sqlalchemy_imports
